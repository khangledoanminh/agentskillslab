#!/usr/bin/env python3
"""doc_coverage: audit coverage documentation thật.

Usage: python3 doc_coverage.py <repo> [--docs-dir DIR] [--output report.json]

Kiểm tra:
- % public functions/classes (không bắt đầu bằng _) có docstring
- % modules có docstring module
- dead internal links trong markdown docs
Output JSON với coverage thật + danh sách missing items (input cho bước generate).
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
import time
from pathlib import Path


def analyze_python(repo: Path) -> dict:
    total_public = 0
    with_doc = 0
    missing: list[dict] = []
    total_modules = 0
    modules_with_doc = 0

    for f in repo.rglob("*.py"):
        parts = f.relative_to(repo).parts
        if any(p.startswith(".") or p in {"__pycache__", "venv", ".venv", "node_modules"} for p in parts):
            continue
        if f.name.startswith(("test_", "conftest")):
            continue
        try:
            tree = ast.parse(f.read_text(encoding="utf-8", errors="replace"))
        except (SyntaxError, OSError):
            continue
        total_modules += 1
        doc = ast.get_docstring(tree)
        if doc:
            modules_with_doc += 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.name.startswith("_"):
                    continue
                total_public += 1
                if ast.get_docstring(node):
                    with_doc += 1
                else:
                    missing.append({"kind": type(node).__name__.lower(),
                                    "name": node.name,
                                    "file": str(f.relative_to(repo)),
                                    "line": node.lineno})
    return {
        "public_api_total": total_public,
        "public_api_documented": with_doc,
        "public_api_coverage_pct": round(with_doc / total_public * 100, 1) if total_public else 100.0,
        "modules_total": total_modules,
        "modules_documented": modules_with_doc,
        "missing_docstrings": missing[:50],
    }


def check_dead_links(docs_dir: Path) -> list[dict]:
    dead: list[dict] = []
    link_re = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
    for md in docs_dir.rglob("*.md"):
        text = md.read_text(encoding="utf-8", errors="replace")
        for _, target in link_re.findall(text):
            if target.startswith(("http://", "https://", "mailto:")):
                continue  # external — manual verify
            clean = target.split("#")[0]
            if not clean:
                continue
            target_path = (md.parent / clean).resolve()
            if not target_path.exists():
                dead.append({"file": str(md.relative_to(docs_dir)), "link": target})
    return dead


def main() -> int:
    p = argparse.ArgumentParser(description="Documentation coverage audit")
    p.add_argument("repo", help="thư mục repo")
    p.add_argument("--docs-dir", default=None, help="thư mục docs (mặc định: repo)")
    p.add_argument("--output", "-o", default=None)
    args = p.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        print(f"ERROR: '{repo}' không phải thư mục", file=sys.stderr)
        return 1
    docs_dir = Path(args.docs_dir).resolve() if args.docs_dir else repo

    t0 = time.perf_counter()
    py_report = analyze_python(repo)
    dead_links = check_dead_links(docs_dir)

    report = {
        "repo": str(repo),
        "audit_seconds": round(time.perf_counter() - t0, 2),
        "python_api": py_report,
        "dead_internal_links": dead_links[:50],
        "targets": {
            "public_api_coverage_pct": 90.0,
            "dead_internal_links": 0,
        },
    }
    report["targets_met"] = (
        report["python_api"]["public_api_coverage_pct"] >= report["targets"]["public_api_coverage_pct"]
        and len(report["dead_internal_links"]) == 0
    )

    out = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"Public API coverage: {report['python_api']['public_api_coverage_pct']}% "
              f"(target {report['targets']['public_api_coverage_pct']}%) | "
              f"dead links: {len(report['dead_internal_links'])}")
        print(f"Output: {args.output}")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
