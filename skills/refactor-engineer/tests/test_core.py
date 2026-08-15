#!/usr/bin/env python3
"""test_core: chay script core cua skill tren fixtures, assert ket qua thuc."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
SKILL = ROOT / "skills" / "refactor-engineer"
SCRIPT = SKILL / "scripts" / "detect_smells.py"
REPO = ROOT / "fixtures/repos/smell-sample"

PASS = 0
FAIL = 0

def check(cond, msg):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"[PASS] {msg}")
    else:
        FAIL += 1
        print(f"[FAIL] {msg}")

def main():
    if not REPO.exists() and REPO != Path("."):
        print(f"SKIP: fixture khong ton tai: {REPO}")
        return 0
    with tempfile.TemporaryDirectory() as tmpd:
        out = str(Path(tmpd) / "out.json")
        args = ["python3", str(SCRIPT), str(REPO), "--output", out]

        r = subprocess.run(args, capture_output=True, text=True, timeout=300)
        check(r.returncode == 0, f"script chay OK (exit={r.returncode}, stderr={r.stderr[:120]})")
        if r.returncode != 0:
            return 1
        d = json.loads(Path(out).read_text())
        assert d['summary']['god_class'] >= 1, 'khong phat hien god class'
        assert d['summary']['long_function'] >= 1, 'khong phat hien long function'
        assert d['summary']['duplication_groups'] >= 1, 'khong phat hien duplication'

        check(True, "asserts hoan tat")
    print(f"{PASS} PASS, {FAIL} FAIL")
    return 1 if FAIL else 0

if __name__ == "__main__":
    raise SystemExit(main())
