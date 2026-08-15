"""Benchmark fixture: đo thời gian khởi động greet.py."""
import subprocess
import time

def run():
    t0 = time.perf_counter()
    r = subprocess.run(["python3", "scripts/greet.py", "--name", "bench"],
                       capture_output=True, text=True, timeout=30)
    ms = (time.perf_counter() - t0) * 1000
    return {"startup_ms": round(ms, 2)}, None

if __name__ == "__main__":
    extra, _ = run()
    print(extra)
