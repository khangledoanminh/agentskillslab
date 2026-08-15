#!/usr/bin/env python3
"""Test suite cho security-auditor: chạy audit.py trên fixture repo và assert findings.

Chạy: python3 tests/test_audit.py  (từ thư mục gốc skill)
Phụ thuộc fixture: ../../fixtures/repos/vulnerable-sample
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent
PROJECT_ROOT = SKILL_ROOT.parent.parent
FIXTURE_REPO = PROJECT_ROOT / "fixtures" / "repos" / "vulnerable-sample"

EXPECTED_MIN_FINDINGS = 5  # aws-key, generic-key, 2x shell-exec, pickle
KNOWN_FALSE_POSITIVE_RULES = set()  # không có trên fixture này


def main() -> int:
    if not FIXTURE_REPO.is_dir():
        print(f"FAIL: fixture repo không tồn tại: {FIXTURE_REPO}", file=sys.stderr)
        return 1

    out_json = HERE / "findings_test.json"
    r = subprocess.run(
        [sys.executable, str(SKILL_ROOT / "scripts" / "audit.py"),
         str(FIXTURE_REPO), "--output", str(out_json)],
        capture_output=True, text=True, timeout=120,
    )
    if r.returncode != 0:
        print(f"FAIL: audit.py exit {r.returncode}\n{r.stderr}", file=sys.stderr)
        return 1

    data = json.loads(out_json.read_text(encoding="utf-8"))
    findings = data["findings"]

    checks = [
        (len(findings) >= EXPECTED_MIN_FINDINGS,
         f"số findings {len(findings)} >= {EXPECTED_MIN_FINDINGS}"),
        (data["scanned_files"] >= 2,
         f"scanned_files {data['scanned_files']} >= 2"),
        (any(f["rule_id"] == "SEC-001-aws-key" for f in findings),
         "phát hiện SEC-001-aws-key"),
        (any(f["rule_id"] == "SEC-002-pickle" for f in findings),
         "phát hiện SEC-002-pickle"),
        (any(f["severity"] == "CRITICAL" for f in findings),
         "có ít nhất 1 finding CRITICAL"),
    ]

    failed = 0
    for ok, desc in checks:
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {desc}")
        if not ok:
            failed += 1

    # cleanup
    out_json.unlink(missing_ok=True)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
