#!/usr/bin/env python3
"""Sinh tests/*.py cho 9 skill còn lại — mỗi test chạy script core trên fixtures và assert kết quả."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"

TESTS = {
    "codebase-architect": (
        "graph_deps.py",
        "fixtures/repos/multi-module-sample",
        "assert d['cycles'], 'khong phat hien duoc cycle core-services'\n"
        "    assert 'main' in d['adjacency'], 'main khong trong adjacency'\n"
        "    assert 'services' in d['adjacency']['main'], 'main khong phu thuoc services'\n",
        "",
    ),
    "dependency-doctor": (
        "doctor.py",
        "fixtures/repos/vulnerable-sample",
        "types = [f['type'] for f in d['findings']]\n"
        "    assert any(t == 'vulnerable' for t in types), 'khong phat hien vulnerable package'\n"
        "    assert len(d['findings']) >= 3, f'finding it qua it: {len(d[\"findings\"])}'\n",
        "",
    ),
    "performance-engineer": (
        "profile_code.py",
        "fixtures/repos/smell-sample/src/mathutils.py",
        "r = subprocess.run(['python3', SCRIPT, str(ROOT/'fixtures/repos/smell-sample/src/mathutils.py'), '--output', out], capture_output=True, text=True, timeout=180)\n"
        "assert r.returncode == 0, r.stderr\n"
        "d = json.loads(Path(out).read_text())\n"
        "assert d.get('timing_ms', {}).get('median', 0) > 0, 'median_ms phai > 0'\n",
        "",
    ),
    "refactor-engineer": (
        "detect_smells.py",
        "fixtures/repos/smell-sample",
        "    assert d['summary']['god_class'] >= 1, 'khong phat hien god class'\n"
        "    assert d['summary']['long_function'] >= 1, 'khong phat hien long function'\n"
        "    assert d['summary']['duplication_groups'] >= 1, 'khong phat hien duplication'\n",
        "",
    ),
    "test-engineer": (
        "coverage_report.py",
        "fixtures/repos/smell-sample/src",
        "    r = subprocess.run(['python3', SCRIPT, str(ROOT/'fixtures/repos/smell-sample/src'), '--tests-dir', str(ROOT/'fixtures/repos/smell-sample/tests'), '--output', out], capture_output=True, text=True, timeout=180)\n"
        "    assert r.returncode == 0, r.stderr\n"
        "    d = json.loads(Path(out).read_text())\n"
        "    assert 0 < d.get('total_line_pct', 0) <= 100, f'coverage bat thuong: {d.get(\"total_line_pct\")}'\n",
        "",
    ),
    "deep-debugger": (
        "collect_context.py",
        "fixtures/repos/multi-module-sample",
        "    assert 'git_log' in d or 'environment' in d, 'thieu section ket qua'\n"
        "    assert 'python' in d.get('environment', {}), 'thieu environment info'\n",
        "",
    ),
    "repo-resurrection": (
        "audit_state.py",
        "fixtures/repos/vulnerable-sample",
        "    assert d['summary']['missing'] >= 3, 'vulnerable-sample phai thieu nhieu thu (ci/docs/tests/...)'\n"
        "    assert any(c['item'] == 'secret_scan' and c['status'] == 'WARNING' for c in d['checks']), 'khong co secret warning'\n",
        "",
    ),
    "release-engineer": (
        "release_check.py",
        "fixtures/repos/vulnerable-sample",
        "    assert d['release_ready'] is False, 'vulnerable-sample khong the release'\n"
        "    assert d['summary']['fail'] >= 1, 'phai co it nhat 1 check fail'\n",
        "",
    ),
    "documentation-engineer": (
        "doc_coverage.py",
        ".",
        "    assert d['python_api']['public_api_total'] > 0, 'khong dem duoc public api'\n"
        "    assert 0 <= d['python_api']['public_api_coverage_pct'] <= 100, 'coverage % bat thuong'\n",
        "",
    ),
}


def gen(name: str, script: str, repo: str, asserts: str, pre: str) -> Path:
    t = SKILLS / name / "tests" / "test_core.py"
    t.write_text(f'''#!/usr/bin/env python3
"""test_core: chay script core cua skill tren fixtures, assert ket qua thuc."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
SKILL = ROOT / "skills" / "{name}"
SCRIPT = SKILL / "scripts" / "{script}"
REPO = ROOT / "{repo}"

PASS = 0
FAIL = 0

def check(cond, msg):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"[PASS] {{msg}}")
    else:
        FAIL += 1
        print(f"[FAIL] {{msg}}")

def main():
    if not REPO.exists() and REPO != Path("."):
        print(f"SKIP: fixture khong ton tai: {{REPO}}")
        return 0
    with tempfile.TemporaryDirectory() as tmpd:
        out = str(Path(tmpd) / "out.json")
        args = ["python3", str(SCRIPT), str(REPO), "--output", out]
{pre}
        r = subprocess.run(args, capture_output=True, text=True, timeout=300)
        check(r.returncode == 0, f"script chay OK (exit={{r.returncode}}, stderr={{r.stderr[:120]}})")
        if r.returncode != 0:
            return 1
        d = json.loads(Path(out).read_text())
{asserts}
        check(True, "asserts hoan tat")
    print(f"{{PASS}} PASS, {{FAIL}} FAIL")
    return 1 if FAIL else 0

if __name__ == "__main__":
    raise SystemExit(main())
''', encoding="utf-8")
    return t


def main():
    import textwrap
    for name, (script, repo, asserts, pre) in TESTS.items():
        # dict dùng indent tuong doi 4 spaces; test output can indent 8 (def main + with block)
        def reindent(s: str) -> str:
            out_lines = []
            for line in s.split("\n"):
                if not line.strip():
                    out_lines.append("")
                    continue
                stripped = line.lstrip(" ")
                out_lines.append("        " + stripped)
            return "\n".join(out_lines)
        t = gen(name, script, repo, reindent(asserts), reindent(pre) if pre else "")
        print(f"generated {t.relative_to(ROOT)}")


if __name__ == "__main__":
    raise SystemExit(main())
