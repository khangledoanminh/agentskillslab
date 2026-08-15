#!/usr/bin/env python3
"""compare: so sánh 2 kết quả benchmark (before/after) từ profile_code.py.

Usage: python3 compare.py before.json after.json [--threshold 1.2]

Verdict:
- speedup >= threshold (default 1.2 = 20%) → IMPROVED
- speedup < 1/threshold → REGRESSED
- giữa 2 ngưỡng → NOISY (không significant)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description="So sánh 2 benchmark results")
    p.add_argument("before", help="file JSON before")
    p.add_argument("after", help="file JSON after")
    p.add_argument("--threshold", type=float, default=1.2,
                   help="speedup threshold coi là significant (default 1.2 = 20%%)")
    args = p.parse_args()

    before = json.loads(Path(args.before).read_text(encoding="utf-8"))
    after = json.loads(Path(args.after).read_text(encoding="utf-8"))

    b_ms = before["timing_ms"]["median"]
    a_ms = after["timing_ms"]["median"]
    if b_ms <= 0:
        print("ERROR: before median <= 0 — dữ liệu benchmark không hợp lệ", file=sys.stderr)
        return 1

    speedup = b_ms / a_ms
    if speedup >= args.threshold:
        verdict = "IMPROVED"
    elif speedup < 1.0 / args.threshold:
        verdict = "REGRESSED"
    else:
        verdict = "NOISY (không significant trong ngưỡng noise)"

    report = {
        "before_median_ms": round(b_ms, 2),
        "after_median_ms": round(a_ms, 2),
        "speedup": round(speedup, 3),
        "threshold": args.threshold,
        "verdict": verdict,
        "before_p95_ms": before["timing_ms"]["p95"],
        "after_p95_ms": after["timing_ms"]["p95"],
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
