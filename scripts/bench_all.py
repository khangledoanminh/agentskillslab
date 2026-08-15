#!/usr/bin/env python3
"""bench_all: chạy benchmark toàn bộ skill benchmarks + platform benchmarks.

Output: benchmarks/results.json — wall_ms cho mỗi benchmark, chạy 3 lần lấy median.
Dùng từ project root: python3 scripts/bench_all.py
"""
import json
import statistics
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
RESULTS = ROOT / "benchmarks" / "results.json"

RUNS = 3
TIMEOUT = 300


def bench_py(bench_path: Path, label: str) -> dict:
    times = []
    last_out = ""
    for _ in range(RUNS):
        t0 = time.perf_counter()
        r = subprocess.run(
            [sys.executable, str(bench_path)],
            capture_output=True, text=True, timeout=TIMEOUT,
            env=dict(__import__("os").environ, PYTHONPATH=str(ROOT)),
            cwd=str(ROOT))
        ms = (time.perf_counter() - t0) * 1000
        times.append(ms)
        last_out = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
        if r.returncode != 0:
            return {"label": label, "error": r.stderr.strip()[:200],
                    "out": last_out[:200]}
    return {"label": label, "median_ms": round(statistics.median(times), 2),
            "min_ms": round(min(times), 2), "max_ms": round(max(times), 2),
            "out": last_out[:300]}


def platform_benchmarks() -> list:
    """Benchmark platform: validate loop + security scan."""
    out = []
    # validate 10 skills loop
    t0 = time.perf_counter()
    for d in sorted(SKILLS.iterdir()):
        if not d.is_dir():
            continue
        subprocess.run(
            [sys.executable, str(ROOT / "cli" / "agent_skills.py"), "validate", str(d)],
            capture_output=True, text=True, timeout=120,
            env=dict(__import__("os").environ, PYTHONPATH=str(ROOT)))
    out.append({"label": "platform/validate-10-skills (1 loop)",
                "median_ms": round((time.perf_counter() - t0) * 1000, 2)})
    # scan_directory trên project root (security scanner alone)
    t0 = time.perf_counter()
    from lib.security import scan_directory  # noqa: E402
    for _ in range(3):
        list(scan_directory(ROOT / "fixtures" / "repos" / "vulnerable-sample"))
    out.append({"label": "platform/scan-vulnerable-sample (3 loop)",
                "median_ms": round((time.perf_counter() - t0) * 1000 / 3, 2)})
    return out


def main() -> int:
    results = []
    for bench in sorted((ROOT / "benchmarks").rglob("*.py")) if False else []:
        results.append(bench_py(bench, bench.stem))
    for skill_dir in sorted(SKILLS.iterdir()):
        if not skill_dir.is_dir():
            continue
        for bench in sorted((skill_dir / "benchmarks").glob("*.py")):
            results.append(bench_py(bench, f"{skill_dir.name}/{bench.stem}"))
    results.extend(platform_benchmarks())
    ROOT.joinpath("benchmarks").mkdir(exist_ok=True)
    payload = {"generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "runs_per_benchmark": RUNS,
               "python": sys.version.split()[0],
               "benchmarks": results}
    RESULTS.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                       encoding="utf-8")
    for b in results:
        status = f"{b.get('median_ms')}ms" if "median_ms" in b else f"ERROR: {b.get('error', '?')}"
        print(f"{b['label']:<60} {status}")
    print(f"\nĐã lưu {RESULTS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
