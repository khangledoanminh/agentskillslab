# Profiling Tools Reference

## Python

| Tool | Use when | Command |
|------|----------|---------|
| `time.perf_counter` | đo 1 function đơn | manual wrapper |
| `cProfile` | tìm hot function trong program | `python3 -m cProfile -s cumtime script.py` |
| `line_profiler` | tìm hot line trong 1 function | `kernprof -l` |
| `timeit` | so micro-benchmark | `python3 -m timeit` |
| `memray`/`tracemalloc` | memory leak/profile | `python3 -m memray run` |

## Quy tắc đo

- Warmup ≥ 1 lần trước khi đo chính thức
- Iterations ≥ 5, report median + p95
- Cùng machine, cùng environment cho before/after
- Đo production-like workload, không synthetic quá đơn giản

