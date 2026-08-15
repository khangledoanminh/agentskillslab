"""Security pattern detection dùng chung cho validator + security-auditor.

Mỗi rule trả về một finding với: rule_id, severity, file, line, evidence, why.
Không invent findings: chỉ báo cáo pattern khớp thực tế trong file.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

# ---------------------------------------------------------------- findings

SEVERITIES = ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO")


@dataclass
class Finding:
    rule_id: str
    severity: str  # CRITICAL | HIGH | MEDIUM | LOW | INFO
    file: str
    line: int
    evidence: str
    why: str

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "file": self.file,
            "line": self.line,
            "evidence": self.evidence,
            "why": self.why,
        }


def _snip(text: str, max_chars: int = 200) -> str:
    text = text.strip().replace("\n", " ")
    if len(text) > max_chars:
        return text[:max_chars] + "..."
    return text


def _snip_secret(text: str, max_chars: int = 60) -> str:
    """Cắt evidence để không leak giá trị secret thật (T12)."""
    text = text.strip()
    if len(text) > max_chars:
        return text[:max_chars] + "...[SNIPPED]"
    return text


# ---------------------------------------------------------------- rules

# SEC-001: secret patterns
SECRET_PATTERNS: list[tuple[str, re.Pattern, str]] = [
    ("SEC-001-aws-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
     "AWS access key ID format"),
    ("SEC-001-generic-key", re.compile(
        r"(?i)(api[_-]?key|apikey|secret[_-]?key|access[_-]?token)"
        r"\s*[:=]\s*['\"][A-Za-z0-9_\-/+=]{16,}['\"]"),
     "Generic API key/secret assignment"),
    ("SEC-001-private-key", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY"),
     "Embedded private key"),
    ("SEC-001-bearer-token", re.compile(r"(?i)bearer\s+[A-Za-z0-9_\-\.]{20,}"),
     "Bearer token trong source"),
    ("SEC-001-password-literal", re.compile(r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"][^'\"]{4,}['\"]"),
     "Password literal trong source"),
]

# SEC-002: dangerous API usage (Python)
DANGEROUS_API_PATTERNS: list[tuple[str, re.Pattern, str]] = [
    ("SEC-002-shell-exec", re.compile(r"\b(?:os\.system|subprocess\.call|subprocess\.Popen|subprocess\.run)\s*\("),
     "Thực thi lệnh ngoài; kiểm tra shell injection"),
    ("SEC-002-eval-exec", re.compile(r"\b(?:eval|exec)\s*\("),
     "eval/exec chạy code động — vectơ injection nếu input không tin cậy"),
    ("SEC-002-pickle", re.compile(r"\bpickle\.loads?\(|yaml\.load\((?!.*Loader)"),
     "Deserialization không an toàn (pickle, yaml.load không Loader)"),
    ("SEC-002-tempfile-insecure", re.compile(r"tempfile\.mktemp\("),
     "tempfile.mktemp dễ bị race condition"),
    ("SEC-002-hardcoded-url", re.compile(r"https?://[^\s'\"]{10,}"),
     "URL hardcoded — xác nhận không gọi endpoint ngoài dự kiến"),
]

# SEC-003: shell metacharacters / dangerous commands trong scripts
SHELL_DANGEROUS_PATTERNS: list[tuple[str, re.Pattern, str]] = [
    ("SEC-003-rm-rf", re.compile(r"\brm\s+(-[A-Za-z]*r[A-Za-z]*f|(-\w+ )+(-r|-f))\s+(/\s*$|/\*|\$)"),
     "rm -rf nhắm vào root hoặc biến không kiểm soát"),
    ("SEC-003-curl-exec", re.compile(r"(curl|wget)\s+[^|]*\|\s*(?:sh|bash|python)"),
     "Download-and-execute (curl|wget ... | sh) — supply-chain risk"),
    ("SEC-003-sudo", re.compile(r"\bsudo\s+(?!-)(?!true|echo|ls|cat\b)"),
     "sudo với lệnh có side-effect"),
    ("SEC-003-chmod-recursive", re.compile(r"\bchmod\s+-R\s+777\b"),
     "chmod -R 777 mở quyền cho mọi user"),
    ("SEC-003-unsafe-unzip", re.compile(r"(?:unzip|tar|zipfile)\s+[^;]*[^/]\s*$"),
     "Trích xuất archive không kiểm soát path (zip-slip risk)"),
]

# SEC-004: obfuscation markers
OBFUSCATION_PATTERNS: list[tuple[str, re.Pattern, str]] = [
    ("SEC-004-base64-exec", re.compile(r"base64\s+(?:-d|--decode)[^;]{0,80}(?:\|\s*(?:sh|bash)|exec|eval)"),
     "Giải mã base64 rồi thực thi — evasion phổ biến"),
    ("SEC-004-hex-exec", re.compile(r"(?i)(?:\\x[0-9a-f]{2}){8,}"),
     "Chuỗi hex escape dài — có thể là code ẩn"),
    ("SEC-004-rot13-tr", re.compile(r"tr\s+'[A-Za-z]'('[A-Za-z]')?\s+'[A-Za-z]'('[A-Za-z]')?\s*[A-Za-z]{20,}"),
     "Xoay ký tự (rot13) trên chuỗi dài — che giấu nội dung"),
    ("SEC-004-heredoc-exec", re.compile(r"<<-?\s*['\"]?EOF['\"]?\s*.{0,40}\|\s*(?:sh|bash)"),
     "Heredoc qua pipe vào shell — che giấu payload"),
]

# SEC-005: prompt injection indicators trong SKILL.md
PROMPT_INJECTION_PATTERNS: list[tuple[str, re.Pattern, str]] = [
    ("SEC-005-instruction-override", re.compile(
        r"(?i)(ignore\s+(all\s+)?(previous|above)\s+(instructions|rules)|"
        r"disregard\s+(the\s+)?(user|system|above))"),
     "Chỉ dẫn ghi đè instruction — prompt injection"),
    ("SEC-005-role-escalation", re.compile(
        r"(?i)(you are now|pretend you are|"
        r"act as an? (unrestricted|uncensored|admin))\b"),
     "Leo thang vai trò — cố gắng thoát ràng buộc agent"),
    ("SEC-005-data-exfil-instruction", re.compile(
        r"(?i)(send\s+(all|the|user)?\s*(files?|data|context|history)\s+to\s+"
        r"(?:https?://|a\s+server|an?\s+(?:external|remote)))"),
     "Hướng dẫn exfiltrate dữ liệu người dùng"),
]

# SEC-006: path traversal / symlink risks
TRAVERSAL_PATTERNS: list[tuple[str, re.Pattern, str]] = [
    ("SEC-006-path-join-external", re.compile(r"(?:os\.path|pathlib|Path)\s*[\.\(][^)]{0,60}\.\.(?:/|\\\\)"),
     "Tham chiếu .. ra ngoài thư mục — path traversal"),
]


ALL_RULES: dict[str, tuple[list[tuple[str, re.Pattern, str]], str]] = {
    "SEC-001": (SECRET_PATTERNS, "secret detection"),
    "SEC-002": (DANGEROUS_API_PATTERNS, "dangerous API detection"),
    "SEC-003": (SHELL_DANGEROUS_PATTERNS, "dangerous shell patterns"),
    "SEC-004": (OBFUSCATION_PATTERNS, "obfuscation detection"),
    "SEC-005": (PROMPT_INJECTION_PATTERNS, "prompt injection indicators"),
    "SEC-006": (TRAVERSAL_PATTERNS, "path traversal patterns"),
}


def scan_file(path: Path, rel_root: str) -> list[Finding]:
    """Quét một file theo tất cả rule SEC-0xx. Bỏ qua file nhị phân."""
    findings: list[Finding] = []
    try:
        content = path.read_bytes()
    except OSError:
        return findings
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return []  # file nhị phân: không scan text patterns

    lines = text.splitlines()
    for rule_id, (patterns, _why) in ALL_RULES.items():
        for pid, pattern, detail in patterns:
            for lineno, line in enumerate(lines, start=1):
                if pattern.search(line):
                    # SEC-001: cắt evidence để tránh leak secret
                    evidence = _snip_secret(line) if rule_id.startswith("SEC-001") else _snip(line)
                    findings.append(Finding(
                        rule_id=pid,
                        severity="CRITICAL" if rule_id in ("SEC-001", "SEC-004") else
                                 "HIGH" if rule_id in ("SEC-002", "SEC-003", "SEC-005") else "MEDIUM",
                        file=str(Path(rel_root) / path.name),
                        line=lineno,
                        evidence=evidence,
                        why=detail,
                    ))
    return findings


def scan_directory(root: Path, rel_root: str = "") -> list[Finding]:
    """Quét toàn bộ cây thư mục (recursive, theo symlinks KHÔNG — an toàn)."""
    findings: list[Finding] = []
    for path in sorted(root.rglob("*")):
        if path.is_dir() or path.is_symlink():
            continue
        # bỏ qua hidden dirs (venv, .git, node_modules) khi scan
        if any(part.startswith((".", "__")) for part in path.relative_to(root).parts[:-1]):
            continue
        if path.suffix in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg",
                           ".ico", ".pdf", ".zip", ".gz", ".tar", ".woff", ".woff2"):
            continue
        findings.extend(scan_file(path, rel_root or str(root.name)))
    return findings
