#!/usr/bin/env python3
"""mutate: simple mutation testing — thay operators, chạy test suite, báo kill/survive.

Usage: python3 mutate.py <module.py> [--operators aor,ror,lcr,sdl] [--tests-dir DIR] [--output report.json]

Cách hoạt động:
1. Parse module thành AST, tìm các node operator có thể mutate
2. Với MỖI mutant: backup file → áp mutation → chạy test suite → restore
3. Test suite FAIL = mutant KILLED; PASS = mutant SURVIVED
4. Output: mutation score = killed / total

An toàn: luôn restore file gốc sau mỗi mutant (try/finally), không để repo
ở trạng thái mutated khi kết thúc.
"""
from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
import time
from pathlib import Path


def find_mutations(source: str, operators: set[str]) -> list[dict]:
    """Tìm các điểm mutation hợp lệ trong source."""
    tree = ast.parse(source)
    mutations = []

    for node in ast.walk(tree):
        if "aor" in operators and isinstance(node, ast.BinOp):
            if isinstance(node.op, (ast.Add, ast.Sub, ast.Mult)):
                mutations.append({
                    "type": "aor", "line": node.lineno, "col": node.col_offset,
                    "op": type(node.op).__name__,
                })
        if "ror" in operators and isinstance(node, ast.Compare):
            if isinstance(node.ops[0], (ast.Gt, ast.Lt, ast.Eq)):
                mutations.append({
                    "type": "ror", "line": node.lineno, "col": node.col_offset,
                    "op": type(node.ops[0]).__name__,
                })
        if "lcr" in operators and isinstance(node, ast.BoolOp):
            mutations.append({
                "type": "lcr", "line": node.lineno, "col": node.col_offset,
                "op": type(node.op).__name__,
            })
        if "sdl" in operators and isinstance(node, ast.Assign):
            mutations.append({
                "type": "sdl", "line": node.lineno, "col": node.col_offset,
                "op": "Assign",
            })

    return mutations[:50]  # giới hạn số mutant cho runtime hợp lý


def apply_mutation(source_lines: list[str], mut: dict) -> list[str]:
    """Áp mutation lên 1 dòng source (text-level, đơn giản)."""
    lines = list(source_lines)
    idx = mut["line"] - 1
    line = lines[idx]

    if mut["type"] == "aor":
        swaps = {"Add": ("+", "-"), "Sub": ("-", "+"), "Mult": ("*", "/")}
        old, new = swaps.get(mut["op"], ("+", "-"))
        lines[idx] = line.replace(old, new, 1)
    elif mut["type"] == "ror":
        swaps = {"Gt": (">", ">="), "Lt": ("<", "<="), "Eq": ("==", "!=")}
        old, new = swaps.get(mut["op"], (">", ">="))
        lines[idx] = line.replace(old, new, 1)
    elif mut["type"] == "lcr":
        lines[idx] = line.replace(" and ", " or ", 1) if " and " in line else line.replace(" or ", " and ", 1)
    elif mut["type"] == "sdl":
        lines[idx] = "# MUTATED(SDL): " + line.lstrip()
    return lines


def run_tests(tests_dir: Path, timeout: int = 300) -> bool:
    r = subprocess.run(
        [sys.executable, "-m", "pytest", str(tests_dir), "-q", "--no-header", "-x"],
        capture_output=True, text=True, timeout=timeout,
    )
    return r.returncode != 0  # test FAIL = mutant bị kill


def main() -> int:
    p = argparse.ArgumentParser(description="Simple mutation testing")
    p.add_argument("module", help="file module .py cần mutate")
    p.add_argument("--operators", default="aor,ror,lcr",
                   help="operators: aor,ror,lcr,sdl")
    p.add_argument("--tests-dir", default=None, help="thư mục tests")
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("--output", "-o", default=None)
    args = p.parse_args()

    module = Path(args.module).resolve()
    if not module.is_file() or module.suffix != ".py":
        print(f"ERROR: '{module}' không phải file .py", file=sys.stderr)
        return 1

    base = module.parent
    tests_dir = Path(args.tests_dir).resolve() if args.tests_dir else base.parent / "tests"
    if not tests_dir.is_dir():
        print(f"ERROR: tests dir không tồn tại: {tests_dir}", file=sys.stderr)
        return 1

    source = module.read_text(encoding="utf-8")
    mutations = find_mutations(source, set(args.operators.split(",")))
    if not mutations:
        print("Không tìm thấy mutation point nào — module quá đơn giản hoặc operators không match")
        return 0

    source_lines = source.splitlines(keepends=True)
    results = []
    t0 = time.perf_counter()

    for i, mut in enumerate(mutations):
        mutated = apply_mutation(source_lines, mut)
        try:
            module.write_text("".join(mutated), encoding="utf-8")
            killed = run_tests(tests_dir, args.timeout)
        except subprocess.TimeoutExpired:
            killed = False
        finally:
            module.write_text(source, encoding="utf-8")  # luôn restore
        results.append({"#": i + 1, **mut, "killed": killed})
        if (i + 1) % 10 == 0:
            print(f"  đã chạy {i + 1}/{len(mutations)} mutants...")

    killed_n = sum(1 for r_ in results if r_["killed"])
    report = {
        "module": str(module),
        "operators": args.operators,
        "total_mutants": len(mutations),
        "killed": killed_n,
        "survived": len(mutations) - killed_n,
        "mutation_score_pct": round(killed_n / len(mutations) * 100, 1) if mutations else 0.0,
        "wall_seconds": round(time.perf_counter() - t0, 2),
        "mutants": results,
    }

    out = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"Mutation score: {report['mutation_score_pct']}% "
              f"({killed_n} killed / {len(mutations)} total, {report['wall_seconds']}s)")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
