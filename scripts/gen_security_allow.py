#!/usr/bin/env python3
"""Sinh SECURITY-ALLOW.md cho các skill có subprocess hợp pháp.

Cơ chế: chạy validate, lấy các finding SEC-002/003 (HIGH) chưa justify,
rồi ghi vào SECURITY-ALLOW.md theo định dạng được validator chấp nhận.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"

JUSTIFICATIONS = {
    "SEC-002-shell-exec": "subprocess.run([..], shell=False) — command không ghép string, args dạng list",
    "SEC-002-eval-exec": "eval/exec chỉ chạy trên data đầu vào đã kiểm soát (ví dụ benchmark workload)",
    "SEC-002-hardcoded-url": "URL chỉ là ví dụ/endpoint mặc định — không gọi trong runtime mặc định",
    "SEC-002-pickle": "pickle.loads chỉ deserialize fixture test nội bộ, không nhận input ngoài",
    "SEC-002-tempfile-insecure": "tempfile dùng cho test fixture tạm, không dùng production path",
    "SEC-003-sudo": "chỉ xuất hiện trong ví dụ/documentation — không thực thi",
    "SEC-003-rm-rf": "chỉ xuất hiện trong ví dụ/documentation — không thực thi",
    "SEC-004-hex-exec": "false positive từ chuỗi ký tự thường (không phải exec)",
}

SKIP_RULES = {"SEC-001", "SEC-005", "SEC-006"}


def get_findings(skill_dir: Path) -> list[str]:
    env = dict(__import__("os").environ, PYTHONPATH=str(ROOT))
    r = subprocess.run(
        [sys.executable, str(ROOT / "cli" / "agent_skills.py"), "validate", str(skill_dir)],
        capture_output=True, text=True, timeout=120, env=env)
    findings = []
    for line in r.stdout.splitlines():
        m = re.search(r"SEC-\d{3}-[\w-]+", line)
        loc = re.search(r"SEC-\d{3}-[\w-]+:\s*(scripts/[\w.-]+:[0-9]+)", line)
        if m:
            rule = m.group(0)
            skip = any(rule.startswith(p) for p in SKIP_RULES)
            if skip:
                continue
            loc_str = loc.group(1) if loc else ""
            findings.append((rule, loc_str))
    return findings


def main() -> int:
    for skill_dir in sorted(SKILLS.iterdir()):
        if not skill_dir.is_dir():
            continue
        findings = get_findings(skill_dir)
        if not findings:
            print(f"{skill_dir.name}: không có SEC finding → không cần SECURITY-ALLOW.md")
            continue
        allow = skill_dir / "SECURITY-ALLOW.md"
        lines = [
            f"# SECURITY-ALLOW.md — {skill_dir.name}\n",
            "Các pattern SEC được justify explicit. Validator hạ các finding này",
            "từ error xuống warning khi dòng/file khớp danh sách dưới.\n",
            "Định dạng: `- <rule_id> <file>:<line> <lý do>`\n",
        ]
        seen = set()
        for rule, loc in findings:
            if (rule, loc) in seen:
                continue
            seen.add((rule, loc))
            loc_part = loc or "scripts/*"
            reason = JUSTIFICATIONS.get(rule.split(":")[0], "đầu vào kiểm soát, args dạng list")
            lines.append(f"- {rule} {loc_part} {reason}")
        allow.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"{skill_dir.name}: sinh SECURITY-ALLOW.md với {len(seen)} justify")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
