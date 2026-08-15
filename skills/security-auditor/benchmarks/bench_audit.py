"""Benchmark: thời gian audit fixture repo."""
import json
import subprocess
import sys
import time
from pathlib import Path

FIXTURE_REPO = Path(__file__).resolve().parents[3] / "fixtures" / "repos" / "vulnerable-sample"

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit.py"

t0 = time.perf_counter()
r = subprocess.run([sys.executable, str(SCRIPT), str(FIXTURE_REPO)],
                   capture_output=True, text=True, timeout=120)
ms = (time.perf_counter() - t0) * 1000
out = json.loads(r.stdout)
print({"wall_ms": round(ms, 2), "files_scanned": out["scanned_files"],
       "findings": len(out["findings"]), "scan_seconds": out["scan_seconds"]})
