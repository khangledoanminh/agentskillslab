#!/usr/bin/env python3
"""coverage_report: đo line + branch coverage THẬT bằng pytest + coverage.py.

Usage: python3 coverage_report.py <module-dir> [--tests-dir DIR] [--target N] [--output report.json]

Yêu cầu: pytest, pytest-cov (nếu chưa có → thử cài qua uv/pip nếu permission cho phép).
Output JSON: total_line_pct, total_branch_pct, missing_lines theo file, target_met.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path


def ensure_coverage_tools() -> str | None:
    """Đảm bảo pytest-cov có mặt. Trả None hoặc lỗi."""
    try:
        import coverage  # noqa: F401
        return None
    except ImportError:
        pass
    for installer in ("uv", "pip"):
        exe = shutil.which(installer)
        if exe:
            cmd = [exe, "pip", "install", "-q", "pytest-cov"] if installer == "pip" else [
                exe, "pip", "install", "-q", "pytest-cov"]
            subprocess.run(cmd, capture_output=True, timeout=180, check=False)
            try:
                import coverage  # noqa: F401
                return None
            except ImportError:
                continue
    return "không cài được pytest-cov (không có uv/pip hoặc cài thất bại)"


def main() -> int:
    p = argparse.ArgumentParser(description="Đo coverage thật bằng pytest")
    p.add_argument("module_dir", help="thư mục module/source cần đo")
    p.add_argument("--tests-dir", default=None, help="thư mục tests (mặc định: tests/)")
    p.add_argument("--target", type=float, default=80.0, help="line coverage target %%")
    p.add_argument("--output", "-o", default=None)
    args = p.parse_args()

    module_dir = Path(args.module_dir).resolve()
    if not module_dir.is_dir():
        print(f"ERROR: '{module_dir}' không phải thư mục", file=sys.stderr)
        return 1

    tests_dir = Path(args.tests_dir).resolve() if args.tests_dir else module_dir.parent / "tests"
    if not tests_dir.is_dir():
        print(f"ERROR: tests dir không tồn tại: {tests_dir}", file=sys.stderr)
        return 1

    err = ensure_coverage_tools()
    if err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1

    cov_data = tests_dir / ".coverage_report_tmp"
    t0 = time.perf_counter()
    r = subprocess.run(
        [sys.executable, "-m", "pytest", str(tests_dir),
         f"--cov={module_dir}", "--cov-report=json:" + str(cov_data / "cov.json"),
         "--cov-branch", "-q", "--no-header"],
        capture_output=True, text=True, timeout=600,
    )
    wall_s = time.perf_counter() - t0

    report = {
        "module_dir": str(module_dir),
        "tests_dir": str(tests_dir),
        "wall_seconds": round(wall_s, 2),
        "pytest_exit": r.returncode,
        "pytest_output": r.stdout[-3000:],
        "target_line_pct": args.target,
        "target_met": False,
    }

    cov_file = cov_data / "cov.json"
    if cov_file.exists():
        data = json.loads(cov_file.read_text(encoding="utf-8"))
        totals = data["totals"]
        line_pct = round(totals["percent_covered"], 2)
        # schema coverage.json: branch_percent (hoặc branches_covered/branches_valid)
        branch_pct = round(
            totals.get("branch_percent", 0.0)
            or (totals["branches_covered"] / totals["branches_valid"] * 100
                if totals.get("branches_valid") else 0.0), 2)
        report["total_line_pct"] = line_pct
        report["total_branch_pct"] = branch_pct
        report["target_met"] = line_pct >= args.target
        report["files"] = {
            fname: {
                "line_pct": round(info["summary"]["percent_covered"], 2),
                "missing_lines": info["missing_lines"][:50],
            }
            for fname, info in list(data["files"].items())[:30]
        }
    else:
        report["error"] = "không tạo được coverage JSON — pytest output trên"
        report["total_line_pct"] = None
        report["total_branch_pct"] = None

    # cleanup
    try:
        shutil.rmtree(cov_data, ignore_errors=True)
    except OSError:
        pass

    out = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"Coverage: line {report.get('total_line_pct')}% "
              f"(target {args.target}%, met={report['target_met']}) | branch {report.get('total_branch_pct')}%")
        print(f"Output: {args.output}")
    else:
        print(out)
    return 0 if report.get("total_line_pct") is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
