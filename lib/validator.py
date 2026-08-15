"""Validator engine: kiểm skill theo SKILL_SPEC v1.0.

Fail-safe design:
- Thu thập TẤT CẢ lỗi/warning, không exit ở lỗi đầu (D4)
- Mỗi finding có mã lỗi V-xxx để tra cứu docs
- Phân lớp: error / warning / info
- Exit validation với report đầy đủ, không crash với input畸形
"""

from __future__ import annotations

import stat
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from .common import (
    FORBIDDEN_EXTENSIONS,
    MAX_TOTAL_DIR_MB,
    SEMVER_PATTERN,
    SPDX_LICENSES,
    SPEC_VERSION,
    human_size,
)
from .manifest import (
    Manifest,
    parse_frontmatter,
    parse_manifest,
    validate_frontmatter,
)
from .security import Finding, scan_file, scan_directory

# Reference links trong SKILL.md (Markdown): [text](path) — bỏ anchor #...
import re
REF_LINK_RE = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")


@dataclass
class ValidationFinding:
    code: str
    level: str  # error | warning | info
    message: str

    def __str__(self) -> str:
        return f"[{self.level.upper()}] {self.code}: {self.message}"


@dataclass
class ValidationReport:
    skill_dir: str
    findings: list[ValidationFinding] = field(default_factory=list)
    security_findings: list[Finding] = field(default_factory=list)
    passed: bool = True

    @property
    def errors(self) -> list[ValidationFinding]:
        return [f for f in self.findings if f.level == "error"]

    @property
    def warnings(self) -> list[ValidationFinding]:
        return [f for f in self.findings if f.level == "warning"]

    @property
    def infos(self) -> list[ValidationFinding]:
        return [f for f in self.findings if f.level == "info"]

    def add(self, code: str, level: str, message: str) -> None:
        self.findings.append(ValidationFinding(code, level, message))
        if level == "error":
            self.passed = False

    def add_sec(self, finding: Finding) -> None:
        """SEC finding: HIGH/CRITICAL → error (fail), MEDIUM/LOW/INFO → warning.

        Nếu skill có SECURITY-ALLOW.md và finding.line nằm trong một vùng được
        justify (line số trong file), hạ xuống warning kèm lý do từ file.
        Cơ chế này cho phép skill có shell commands hợp pháp nhưng phải
        DOCUMENT explicit — đúng tinh thần 'security rules + deterministic'.
        """
        self.security_findings.append(finding)
        severity = finding.severity.upper()
        allow_path = Path(self.skill_dir) / "SECURITY-ALLOW.md"
        justified = False
        if allow_path.exists() and severity in ("HIGH", "MEDIUM"):
            for line in allow_path.read_text(encoding="utf-8", errors="replace").splitlines():
                s = line.strip()
                if s.startswith("- ") and finding.rule_id in s:
                    # định dạng: - SEC-002-shell-exec scripts/audit.py:14 vì lý do ...
                    if (f"{finding.file}:{finding.line}" in s
                            or f"{finding.file}" in s
                            or s.endswith("scripts/*")):
                        justified = True
                        break
        if severity in ("CRITICAL", "HIGH") and not justified:
            self.add(
                finding.rule_id,
                "error",
                f"{finding.file}:{finding.line} — {finding.evidence} ({finding.why})",
            )
        else:
            label = "warning" if justified else ("warning" if severity in ("MEDIUM", "LOW") else "info")
            why_note = " — đã justify trong SECURITY-ALLOW.md" if justified else ""
            self.add(
                finding.rule_id,
                label,
                f"{finding.file}:{finding.line} — {finding.evidence} ({finding.why}){why_note}",
            )

    def to_dict(self) -> dict:
        return {
            "skill_dir": self.skill_dir,
            "passed": self.passed,
            "errors": len(self.errors),
            "warnings": len(self.warnings),
            "info": len(self.infos),
            "findings": [str(f) for f in self.findings],
            "security_findings": [f.to_dict() for f in self.security_findings],
        }


def _check_references(skill_md: Path, skill_dir: Path) -> list[str]:
    """V-014: mọi file được tham chiếu trong SKILL.md phải tồn tại."""
    errors: list[str] = []
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    seen: set[str] = set()
    for rel in REF_LINK_RE.findall(text):
        if rel.startswith("http://") or rel.startswith("https://") or rel.startswith("mailto:"):
            continue
        if rel in seen:
            continue
        seen.add(rel)
        target = (skill_dir / rel).resolve()
        skill_real = skill_dir.resolve()
        if not str(target).startswith(str(skill_real)):
            errors.append(f"V-014: tham chiếu '{rel}' trỏ ra ngoài skill dir (path traversal)")
            continue
        if not target.exists():
            errors.append(f"V-014: file tham chiếu '{rel}' không tồn tại")
    return errors


def _syntax_check_scripts(skill_dir: Path) -> list[str]:
    """V-013: scripts phải syntax-check được."""
    errors: list[str] = []
    scripts = skill_dir / "scripts"
    if not scripts.is_dir():
        return errors
    for path in sorted(scripts.rglob("*")):
        if path.is_dir():
            continue
        if path.suffix == ".py":
            try:
                subprocess.run(
                    [sys.executable, "-m", "py_compile", str(path)],
                    check=True, capture_output=True, timeout=60,
                )
            except subprocess.CalledProcessError:
                errors.append(f"V-013: scripts/{path.relative_to(scripts)} có lỗi syntax Python")
            except subprocess.TimeoutExpired:
                errors.append(f"V-013: scripts/{path.relative_to(scripts)} compile quá 60s")
        elif path.suffix == ".sh":
            try:
                subprocess.run(
                    ["bash", "-n", str(path)], check=True, capture_output=True, timeout=60,
                )
            except subprocess.CalledProcessError:
                errors.append(f"V-013: scripts/{path.relative_to(scripts)} có lỗi syntax bash")
            except FileNotFoundError:
                errors.append(f"V-013: không có bash để kiểm syntax {path.name}")
            except subprocess.TimeoutExpired:
                errors.append(f"V-013: scripts/{path.relative_to(scripts)} check quá 60s")
    return errors


def validate_skill(skill_dir: Path) -> ValidationReport:
    """Validate toàn diện một skill dir. Không throw exception; luôn trả report."""
    try:
        abs_skill_dir = Path(skill_dir).resolve()
    except OSError as exc:
        report = ValidationReport(skill_dir=str(skill_dir))
        report.add("V-000", "error", f"không resolve được đường dẫn: {exc}")
        return report
    report = ValidationReport(skill_dir=str(abs_skill_dir))

    try:
        skill_dir = abs_skill_dir
    except OSError as exc:
        report.add("V-000", "error", f"không resolve được đường dẫn: {exc}")
        return report

    if not skill_dir.is_dir():
        report.add("V-000", "error", f"'{skill_dir}' không phải thư mục")
        return report

    # --- giới hạn kích thước tổng (T8 resource exhaustion)
    try:
        total = sum(
            f.stat().st_size
            for f in skill_dir.rglob("*")
            if f.is_file() and not f.is_symlink()
        )
    except OSError:
        total = -1
    if total > MAX_TOTAL_DIR_MB * 1024 * 1024:
        report.add("V-000", "error",
                   f"tổng kích thước skill dir {human_size(total)} vượt giới hạn {MAX_TOTAL_DIR_MB} MiB")

    # --- V-001/V-002: SKILL.md + frontmatter
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        report.add("V-001", "error", "thiếu file bắt buộc SKILL.md")
        return report  # không có SKILL.md thì dừng sớm

    fm, error = parse_frontmatter(skill_md)
    if error or fm is None:
        report.add("V-002", "error", f"frontmatter SKILL.md: {error}")
        return report
    report.add("V-002", "info", "frontmatter hợp lệ")

    for err in validate_frontmatter(fm, skill_dir.name):
        code = err.split(":")[0].strip()
        report.add(code, "error", err.split(": ", 1)[1] if ": " in err else err)

    # --- V-005..V-009: skill.yaml + manifest
    yaml_path = skill_dir / "skill.yaml"
    manifest: Manifest | None = None
    if not yaml_path.exists():
        report.add("V-005", "error", "thiếu skill.yaml (bắt buộc với spec ASL 1.0)")
    else:
        manifest, error = parse_manifest(yaml_path)
        if error or manifest is None:
            report.add("V-005", "error", f"skill.yaml: {error}")
            manifest = None
        else:
            report.add("V-005", "info", "skill.yaml parse thành công")

    if manifest is not None:
        if manifest.format_version != SPEC_VERSION:
            report.add("V-006", "error",
                       f"format_version='{manifest.format_version}' không khớp spec {SPEC_VERSION}")
        else:
            report.add("V-006", "info", f"format_version {SPEC_VERSION} OK")

        if not manifest.version or not SEMVER_PATTERN.match(manifest.version):
            report.add("V-007", "error", "version thiếu hoặc không đúng semver")

        if not manifest.title:
            report.add("V-000", "error", "skill.yaml thiếu title")

        lic = manifest.license or ""
        if lic not in SPDX_LICENSES:
            report.add("V-008", "error",
                       f"license='{lic}' không phải SPDX identifier hợp lệ "
                       f"(VD: MIT, Apache-2.0)")

        perms = manifest.permissions
        for req in ("filesystem", "network", "downloads", "install_packages", "subprocess"):
            if req not in perms:
                report.add("V-009", "error", f"permissions thiếu trường '{req}'")
        for req in ("filesystem", "network", "subprocess"):
            pass  # enum check nằm ở parse; giữ đơn giản

        # V-016: compatibility claim
        agents = manifest.declared_agents
        for agent in agents:
            if agent not in {
                "claude-code", "codex", "cursor", "github-copilot", "opencode",
                "kilo", "cline", "aider", "vscode-agent", "manus",
            }:
                report.add("V-016", "warning", f"compatibility.agents chứa agent không chuẩn: {agent}")

    # --- V-010: name consistency đã check ở validate_frontmatter

    # --- V-011: không file thực thi ở root
    try:
        for entry in skill_dir.iterdir():
            if entry.is_file() and not entry.is_symlink():
                try:
                    mode = entry.stat().st_mode
                except OSError:
                    continue
                if entry.name in ("SKILL.md", "skill.yaml", "README.md",
                                  "requirements.txt", "LICENSE"):
                    continue
                if mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
                    report.add("V-011", "error",
                               f"file thực thi ở root skill dir: {entry.name} (chuyển vào scripts/)")
    except OSError:
        pass

    # --- V-013: syntax check scripts
    for err in _syntax_check_scripts(skill_dir):
        report.findings.append(ValidationFinding(
            err.split(":")[0].strip(), "error", err.split(": ", 1)[1] if ": " in err else err))
        report.passed = False

    # --- V-014: reference links
    for err in _check_references(skill_md, skill_dir):
        code = err.split(":")[0].strip()
        report.findings.append(ValidationFinding(
            code, "error", err.split(": ", 1)[1] if ": " in err else err))
        report.passed = False

    # --- V-015: scan security patterns trên scripts/ và skill.yaml
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.is_dir():
        for finding in scan_directory(scripts_dir):
            report.add_sec(finding)
    for finding in scan_file(yaml_path, rel_root=skill_dir.name) if yaml_path.exists() else []:
        report.add_sec(finding)
    # scan cả SKILL.md body (chỉ SEC-005 prompt injection; bỏ SEC-001 vì description có thể dài)
    from .security import ALL_RULES
    body_text = skill_md.read_text(encoding="utf-8", errors="replace")
    for lineno, line in enumerate(body_text.splitlines(), start=1):
        for pid, pattern, detail in ALL_RULES["SEC-005"][0]:
            if pattern.search(line):
                report.add_sec(Finding(
                    rule_id=pid, severity="HIGH",
                    file="SKILL.md", line=lineno,
                    evidence=line.strip()[:120],
                    why=f"{detail} — prompt injection indicator",
                ))

    # --- V-020: tests/ bắt buộc nếu scripts/ không rỗng
    has_scripts = bool(scripts_dir.is_dir() and any(scripts_dir.iterdir()))
    tests_dir = skill_dir / "tests"
    if has_scripts and (not tests_dir.is_dir() or not any(tests_dir.iterdir())):
        report.add("V-020", "error", "skill có scripts/ nhưng thiếu tests/")

    # --- V-022: forbidden file types trong assets/references
    for subdir in ("assets", "references"):
        d = skill_dir / subdir
        if d.is_dir():
            for f in d.rglob("*"):
                if f.is_file() and not f.is_symlink() and f.suffix.lower() in FORBIDDEN_EXTENSIONS:
                    report.add("V-022", "error", f"{subdir}/{f.name}: file thực thi/binary bị cấm")

    # --- V-023: symlinks ra ngoài skill dir
    real = skill_dir.resolve()
    for f in skill_dir.rglob("*"):
        try:
            if f.is_symlink():
                target = f.resolve()
                if not str(target).startswith(str(real)):
                    report.add("V-023", "error",
                               f"symlink '{f.relative_to(skill_dir)}' trỏ ra ngoài skill dir")
        except OSError:
            report.add("V-023", "error", f"symlink '{f.relative_to(skill_dir)}' lỗi khi resolve")

    # --- V-019: body size info
    try:
        body = skill_md.read_text(encoding="utf-8", errors="replace")
        tokens_est = len(body.split()) * 1.3
        if tokens_est > 5000:
            report.add("V-019", "info",
                       f"body SKILL.md ~{int(tokens_est)} tokens (>5000 khuyến nghị tách file tham chiếu)")
    except OSError:
        pass

    return report
