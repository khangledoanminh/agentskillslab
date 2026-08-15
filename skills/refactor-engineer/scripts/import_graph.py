#!/usr/bin/env python3
"""import_graph: xây dependency graph từ import statements, phát hiện cycle.

Usage: python3 import_graph.py <repo> [--output graph.json]

Output JSON: adjacency list module → modules nó import, cycles (list),
Ca/Ce metrics. Dùng thật: parse AST import statements.
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
import time
from collections import defaultdict
from pathlib import Path


def module_name(repo: Path, f: Path) -> str:
    rel = f.relative_to(repo).with_suffix("")
    parts = rel.parts
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts) if parts else "<root>"


def build_graph(repo: Path, group_packages: bool = True) -> tuple[dict[str, set[str]], dict[str, str]]:
    graph: dict[str, set[str]] = defaultdict(set)
    files: dict[str, Path] = {}
    for f in repo.rglob("*.py"):
        rel_parts = f.relative_to(repo).parts
        if any(p.startswith(".") for p in rel_parts):
            continue
        name = module_name(repo, f)
        files[name] = f
        try:
            tree = ast.parse(f.read_text(encoding="utf-8", errors="replace"))
        except (SyntaxError, OSError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    graph[name].add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    graph[name].add(node.module)

    # giữ lại chỉ edge tới module nội bộ thật (có file tương ứng)
    internal = {k: {v for v in vs if v in files} for k, vs in graph.items()}

    if group_packages:
        grouped: dict[str, set[str]] = defaultdict(set)
        pkg_of = {k: k.split(".")[0] if "." in k else k for k in internal}
        for k, vs in internal.items():
            for v in vs:
                dep_pkg = pkg_of.get(v, v.split(".")[0] if "." in v else v)
                src_pkg = pkg_of.get(k, k.split(".")[0] if "." in k else k)
                if src_pkg != dep_pkg:
                    grouped[src_pkg].add(dep_pkg)
        return grouped, {k: str(v.relative_to(repo)) for k, v in files.items()}
    return internal, {k: str(v.relative_to(repo)) for k, v in files.items()}


def find_cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    """DFS tìm tất cả cycle cơ bản."""
    cycles: list[list[str]] = []
    visited: set[str] = set()

    def dfs(node: str, path: list[str], path_set: set[str]):
        for dep in graph.get(node, set()):
            if dep in path_set:
                idx = path.index(dep)
                cycle = path[idx:] + [dep]
                canonical = tuple(sorted(set(cycle)))
                if canonical not in {tuple(sorted(set(c))) for c in cycles}:
                    cycles.append(cycle)
            elif dep not in visited:
                dfs(dep, path + [dep], path_set | {dep})
        visited.add(node)

    for node in graph:
        if node not in visited:
            dfs(node, [node], {node})
    return cycles


def metrics(graph: dict[str, set[str]]) -> dict[str, dict]:
    ca: dict[str, int] = defaultdict(int)
    for node, deps in graph.items():
        for dep in deps:
            ca[dep] += 1
    return {
        node: {"Ca": ca.get(node, 0), "Ce": len(deps)}
        for node, deps in graph.items()
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Import dependency graph + cycle detection")
    p.add_argument("repo", help="thư mục repo")
    p.add_argument("--output", "-o", default=None)
    args = p.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        print(f"ERROR: '{repo}' không phải thư mục", file=sys.stderr)
        return 1

    t0 = time.perf_counter()
    graph, filemap = build_graph(repo)
    cycles = find_cycles(graph)
    met = metrics(graph)

    report = {
        "repo": str(repo),
        "modules": len(graph),
        "build_seconds": round(time.perf_counter() - t0, 2),
        "adjacency": {k: sorted(v) for k, v in graph.items()},
        "cycles": cycles,
        "metrics": met,
        "filemap": filemap,
    }

    out = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"Modules: {report['modules']} | Cycles: {len(cycles)} | {report['build_seconds']}s")
        print(f"Output: {args.output}")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
