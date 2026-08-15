#!/usr/bin/env python3
"""detect_smells: phát hiện code smells bằng static analysis thật.

Usage: python3 detect_smells.py <repo> [--thresholds FILE] [--output smells.json]

Smells phát hiện (xem references/SMELL-CATALOG.md):
- God class: class > 500 dòng HOẶC > 15 methods HOẶC > 10 attributes
- Long function: > 50 dòng HOẶC nested > 4
- Duplication: đoạn code trùng (normalized) giữa các file
Output JSON với severity và evidence line numbers.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
import time
from pathlib import Path

DEFAULT_THRESHOLDS = {
    "god_class_lines": 500,
    "god_class_methods": 15,
    "god_class_attributes": 10,
    "long_function_lines": 50,
    "long_function_nesting": 4,
    "duplication_min_lines": 6,
}


def classify_god_class(node: ast.ClassDef, source_lines: list[str], th: dict) -> dict | None:
    methods = [n for n in ast.walk(node) if isinstance(n, ast.FunctionDef)]
    attrs = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Assign):
            for target in n.targets:
                if isinstance(target, ast.Name):
                    attrs.add(target.id)
    line_span = node.end_lineno - node.lineno + 1 if node.end_lineno else 0

    reasons = []
    if line_span >= th["god_class_lines"]:
        reasons.append(f"{line_span} dòng (threshold {th['god_class_lines']})")
    if len(methods) >= th["god_class_methods"]:
        reasons.append(f"{len(methods)} methods (threshold {th['god_class_methods']})")
    if len(attrs) >= th["god_class_attributes"]:
        reasons.append(f"{len(attrs)} attributes (threshold {th['god_class_attributes']})")

    if not reasons:
        return None
    return {
        "smell": "god_class", "severity": "HIGH", "file": None,
        "name": node.name, "line": node.lineno,
        "detail": "; ".join(reasons),
    }


def classify_long_function(node: ast.FunctionDef, th: dict) -> dict | None:
    line_span = (node.end_lineno - node.lineno + 1) if node.end_lineno else 0
    max_nesting = 0

    def walk(n: ast.AST, depth: int):
        nonlocal max_nesting
        for child in ast.iter_child_nodes(n):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                walk(child, depth + 1)
            else:
                walk(child, depth)
        if isinstance(n, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
            max_nesting = max(max_nesting, depth)

    walk(node, 0)

    reasons = []
    if line_span >= th["long_function_lines"]:
        reasons.append(f"{line_span} dòng (threshold {th['long_function_lines']})")
    if max_nesting >= th["long_function_nesting"]:
        reasons.append(f"nesting {max_nesting} (threshold {th['long_function_nesting']})")
    if not reasons:
        return None
    return {
        "smell": "long_function", "severity": "MEDIUM", "file": None,
        "name": node.name, "line": node.lineno, "detail": "; ".join(reasons),
    }


def duplication_hashes(repo: Path, th: dict) -> list[dict]:
    """Normalized duplication detection: hashing segments dòng code (bỏ comment/whitespace)."""
    segments: dict[str, list[tuple[str, int]]] = {}
    files = sorted([f for f in repo.rglob("*.py")
                    if not any(p.startswith(".") for p in f.relative_to(repo).parts)])
    for f in files:
        try:
            tree = ast.parse(f.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        source = f.read_text(encoding="utf-8", errors="replace").splitlines()
        # segment theo function body
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.end_lineno:
                body_lines = []
                for ln in range(node.lineno, node.end_lineno + 1):
                    if ln - 1 < len(source):
                        body_lines.append(normalize(source[ln - 1]))
                seg = "\n".join(body_lines)
                if seg:
                    h = hashlib.sha256(seg.encode()).hexdigest()[:16]
                    segments.setdefault(h, []).append((str(f.relative_to(repo)), node.lineno))

    findings = []
    for h, locs in segments.items():
        if len(locs) >= 2:
            findings.append({
                "smell": "duplication", "severity": "MEDIUM",
                "locations": [{"file": f, "line": ln} for f, ln in locs],
                "detail": f"{len(locs)} occurrences trùng nhau",
            })
    return findings


def normalize(line: str) -> str:
    line = line.split("#")[0].strip()
    return " ".join(line.split())


def main() -> int:
    p = argparse.ArgumentParser(description="Phát hiện code smells")
    p.add_argument("repo", help="thư mục repo")
    p.add_argument("--thresholds", default=None, help="file JSON override thresholds")
    p.add_argument("--output", "-o", default=None)
    args = p.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        print(f"ERROR: '{repo}' không phải thư mục", file=sys.stderr)
        return 1

    th = dict(DEFAULT_THRESHOLDS)
    if args.thresholds:
        th.update(json.loads(Path(args.thresholds).read_text(encoding="utf-8")))

    smells: list[dict] = []
    t0 = time.perf_counter()
    files = sorted([f for f in repo.rglob("*.py")
                    if not any(p.startswith((".", "__")) for p in f.relative_to(repo).parts[:-1])
                    and not f.name.startswith(("test_", "conftest"))])
    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(text)
            source_lines = text.splitlines()
        except (SyntaxError, OSError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                g = classify_god_class(node, source_lines, th)
                if g:
                    g["file"] = str(f.relative_to(repo))
                    smells.append(g)
            elif isinstance(node, ast.FunctionDef):
                lf = classify_long_function(node, th)
                if lf:
                    lf["file"] = str(f.relative_to(repo))
                    smells.append(lf)

    smells.extend(duplication_hashes(repo, th))

    report = {
        "repo": str(repo),
        "files_scanned": len(files),
        "scan_seconds": round(time.perf_counter() - t0, 2),
        "smells": smells,
        "summary": {
            "god_class": sum(1 for s in smells if s["smell"] == "god_class"),
            "long_function": sum(1 for s in smells if s["smell"] == "long_function"),
            "duplication_groups": sum(1 for s in smells if s["smell"] == "duplication"),
        },
    }

    out = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"Smells: {len(smells)} "
              f"(god_class={report['summary']['god_class']}, "
              f"long_function={report['summary']['long_function']}, "
              f"duplication={report['summary']['duplication_groups']})")
        print(f"Output: {args.output}")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
