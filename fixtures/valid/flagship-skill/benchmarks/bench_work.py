import subprocess, time
t0 = time.perf_counter()
subprocess.run(['python3', 'scripts/work.py', 'b'], capture_output=True, timeout=30)
print({'ms': round((time.perf_counter()-t0)*1000, 2)})
