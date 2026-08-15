#!/usr/bin/env python3
"""profile_code: benchmark + profile workload thật.

Usage: python3 profile_code.py <target-script.py> [--args "..."] [--iterations N] [--output profile.json]

Output JSON: timing (median, min, max, p95 ms), cProfile top-10 functions,
environment info. Mọi số liệu đo thật bằng time.perf_counter + cProfile.
"""
from __future__ import annotations

import argparse
import cProfile
import io
import json
import os
import pstats
import subprocess
import sys
import time
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description="Benchmark + profile workload thật")
    p.add_argument("target", help="file script Python workload cần profile")
    p.add_argument("--args", default="", help="argument truyền cho target script")
    p.add_argument("--iterations", type=int, default=5)
    p.add_argument("--warmup", type=int, default=1)
    p.add_argument("--top", type=int, default=10, help="số function top trong profile")
    p.add_argument("--output", "-o", default=None)
    args = p.parse_args()

    target = Path(args.target).resolve()
    if not target.is_file() or target.suffix != ".py":
        print(f"ERROR: '{target}' không phải file .py", file=sys.stderr)
        return 1

    cmd = [sys.executable, str(target)] + args.args.split()

    times: list[float] = []
    for i in range(args.warmup + args.iterations):
        t0 = time.perf_counter()
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        t1 = time.perf_counter()
        if i >= args.warmup:
            times.append((t1 - t0) * 1000)
        if r.returncode != 0:
            print(f"WARNING: target exit {r.returncode}: {r.stderr[:300]}", file=sys.stderr)

    s = sorted(times)
    n = len(s)
    median = s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2
    p95 = s[int(n * 0.95)] if n else 0

    # cProfile trên 1 iteration riêng
    prof = cProfile.Profile()
    prof.enable()
    subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    prof.disable()
    buf = io.StringIO()
    ps = pstats.Stats(prof, stream=buf).sort_stats("cumulative")
    ps.print_stats(args.top)
    profile_text = buf.getvalue()

    top_funcs: list[dict] = []
    for line in profile_text.splitlines()[6:6 + args.top]:
        parts = line.split(None, 6)
        if len(parts) >= 7:
            top_funcs.append({
                "ncalls": parts[0], "tottime": parts[1], "cumtime": parts[3],
                "function": parts[6][:120],
            })

    report = {
        "target": str(target),
        "args": args.args,
        "iterations": args.iterations,
        "warmup": args.warmup,
        "timing_ms": {
            "median": round(median, 2), "min": round(min(times), 2),
            "max": round(max(times), 2), "p95": round(p95, 2),
        },
        "environment": {
            "os": os.uname().sysname,
            "python": sys.version.split()[0],
            "cpu_count": os.cpu_count(),
        },
        "profile_top": top_funcs,
        "profile_raw_head": profile_text[:2000],
    }

    out = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"Timing: median {report['timing_ms']['median']}ms | p95 {report['timing_ms']['p95']}ms")
        print(f"Output: {args.output}")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
