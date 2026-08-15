#!/usr/bin/env python3
"""check_examples: chạy mọi code block python trong markdown docs, verify exit code.

Usage: python3 check_examples.py <docs-dir>

Rule: example không chạy được worse hơn không có example. Code block ```python
hoặc ```bash được trích và thực thi trong temp dir (để file write an toàn).
Block chỉ illustration (không phải instruction) đánh dấu <!-- example:skip -->.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path


BLOCK_RE = re.compile(r"```(python|bash|sh)\n(.*?)```", re.DOTALL)
SKIP_MARKER = "<!-- example:skip -->"


def extract_examples(md: Path) -> list[dict]:
    text = md.read_text(encoding="utf-8", errors="replace")
    examples = []
    for i, m in enumerate(BLOCK_RE.finditer(text)):
        lang, code = m.group(1), m.group(2).strip()
        # block ngay sau SKIP_MARKER trong cùng đoạn → skip
        before = text[:m.start()]
        if before.rstrip().endswith(SKIP_MARKER):
            continue
        if not code:
            continue
        examples.append({"index": i + 1, "lang": lang, "code": code,
                         "line": text[:m.start()].count("\n") + 1})
    return examples


def run_example(example: dict) -> dict:
    lang, code = example["lang"], example["code"]
    with tempfile.TemporaryDirectory() as td:
        if lang == "python":
            script = Path(td) / "example.py"
            script.write_text(code, encoding="utf-8")
            r = subprocess.run([sys.executable, str(script)], cwd=td,
                               capture_output=True, text=True, timeout=120)
            return {"lang": "python", "exit": r.returncode,
                    "stderr": r.stderr[:300], "stdout": r.stdout[:200]}
        r = subprocess.run(["bash", "-e"], input=code, cwd=td,
                           capture_output=True, text=True, timeout=120)
        return {"lang": "bash", "exit": r.returncode,
                "stderr": r.stderr[:300], "stdout": r.stdout[:200]}


def main() -> int:
    p = argparse.ArgumentParser(description="Verify runnable examples trong docs")
    p.add_argument("docs_dir", help="thư mục docs")
    p.add_argument("--output", "-o", default=None)
    args = p.parse_args()

    docs_dir = Path(args.docs_dir).resolve()
    if not docs_dir.is_dir():
        print(f"ERROR: '{docs_dir}' không phải thư mục", file=sys.stderr)
        return 1

    results: list[dict] = []
    t0 = time.perf_counter()
    for md in sorted(docs_dir.rglob("*.md")):
        for ex in extract_examples(md):
            res = run_example(ex)
            results.append({"file": str(md.relative_to(docs_dir)),
                            "line": ex["line"], "lang": ex["lang"],
                            "exit": res["exit"],
                            "pass": res["exit"] == 0,
                            "stderr_head": res["stderr"]})

    passed = sum(1 for r_ in results if r_["pass"])
    report = {
        "docs_dir": str(docs_dir),
        "check_seconds": round(time.perf_counter() - t0, 2),
        "examples_total": len(results),
        "examples_pass": passed,
        "results": results,
    }

    out = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"Examples: {passed}/{len(results)} pass | {report['check_seconds']}s")
        print(f"Output: {args.output}")
    else:
        print(out)
    return 0 if len(results) == 0 or all(r_["pass"] for r_ in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
