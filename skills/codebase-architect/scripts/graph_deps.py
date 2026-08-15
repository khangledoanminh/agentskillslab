#!/usr/bin/env python3
"""graph_deps: xây dependency graph thật từ import statements + sinh Mermaid diagram.

Usage: python3 graph_deps.py <repo> [--language python] [--output graph.json] [--diagram diagram.mmd]

Diagram Mermaid sinh TỰ ĐỘNG từ adjacency list — validate roundtrip bằng
scripts/verify_diagram.py (parse lại diagram phải khớp graph gốc).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "refactor-engineer" / "scripts"))
from import_graph import build_graph, find_cycles, metrics  # noqa: E402


def generate_mermaid(graph: dict[str, set[str]]) -> str:
    lines = ["flowchart TD"]
    for node in sorted(graph):
        safe = node.replace(".", "_").replace("-", "_")
        lines.append(f"    {safe}[\"{node}\"]")
    for node, deps in sorted(graph.items()):
        src = node.replace(".", "_").replace("-", "_")
        for dep in sorted(deps):
            dst = dep.replace(".", "_").replace("-", "_")
            lines.append(f"    {src} -->|import| {dst}")
    return "\n".join(lines) + "\n"


def main() -> int:
    p = argparse.ArgumentParser(description="Dependency graph + Mermaid diagram")
    p.add_argument("repo", help="thư mục repo")
    p.add_argument("--language", default="python")
    p.add_argument("--output", "-o", default=None)
    p.add_argument("--diagram", "-d", default=None, help="file output Mermaid .mmd")
    args = p.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        print(f"ERROR: '{repo}' không phải thư mục", file=sys.stderr)
        return 1

    t0 = time.perf_counter()
    graph, filemap = build_graph(repo)
    cycles = find_cycles(graph)
    met = metrics(graph)

    # hotspots: Ca cao nhất
    hotspots = sorted(met.items(), key=lambda kv: -kv[1]["Ca"])[:5]

    report = {
        "repo": str(repo),
        "language": args.language,
        "modules": len(graph),
        "edges": sum(len(v) for v in graph.values()),
        "build_seconds": round(time.perf_counter() - t0, 2),
        "adjacency": {k: sorted(v) for k, v in graph.items()},
        "cycles": cycles,
        "metrics": met,
        "hotspots": [{"module": m, "Ca": v["Ca"], "Ce": v["Ce"]} for m, v in hotspots],
    }

    out = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"Graph: {report['modules']} modules, {report['edges']} edges, "
              f"{len(cycles)} cycles | {report['build_seconds']}s")
        print(f"Output: {args.output}")
    else:
        print(out)

    if args.diagram:
        Path(args.diagram).write_text(generate_mermaid(graph), encoding="utf-8")
        print(f"Diagram Mermaid: {args.diagram}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
