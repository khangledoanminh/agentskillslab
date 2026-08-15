"""Benchmark framework — đo hiệu năng THẬT, không fabricate số liệu.

Nguyên tắc:
- time.perf_counter cho wall-clock, resource.getrusage cho CPU
- Mọi phép đo chạy nhiều iteration và lấy median (chống noise)
- Kết quả in ra kèm unit và môi trường (OS, Python version, CPU count)
"""

from __future__ import annotations

import platform
import resource
import time
from dataclasses import dataclass, field


@dataclass
class BenchmarkResult:
    name: str
    iterations: int
    times_ms: list[float] = field(default_factory=list)
    extra: dict = field(default_factory=dict)

    @property
    def median_ms(self) -> float:
        if not self.times_ms:
            return 0.0
        s = sorted(self.times_ms)
        n = len(s)
        return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2

    @property
    def min_ms(self) -> float:
        return min(self.times_ms) if self.times_ms else 0.0

    @property
    def max_ms(self) -> float:
        return max(self.times_ms) if self.times_ms else 0.0

    @property
    def p95_ms(self) -> float:
        if not self.times_ms:
            return 0.0
        s = sorted(self.times_ms)
        return s[int(len(s) * 0.95)] if s else 0.0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "iterations": self.iterations,
            "median_ms": round(self.median_ms, 2),
            "min_ms": round(self.min_ms, 2),
            "max_ms": round(self.max_ms, 2),
            "p95_ms": round(self.p95_ms, 2),
            **self.extra,
        }


def environment_info() -> dict:
    try:
        cpu_count = len(__import__("os").sched_getaffinity(0))
    except (AttributeError, OSError):
        cpu_count = __import__("os").cpu_count() or 1
    return {
        "os": platform.system(),
        "os_release": platform.release(),
        "python": platform.python_version(),
        "cpu_count": cpu_count,
    }


def bench(func, *, iterations: int = 5, warmup: int = 1, name: str = "benchmark") -> BenchmarkResult:
    """Chạy func nhiều lần, warmup trước, lấy median.

    func() -> (result, extra_dict) hoặc chỉ result.
    """
    result = BenchmarkResult(name=name, iterations=iterations)
    for _ in range(warmup):
        func()
    for _ in range(iterations):
        t0 = time.perf_counter()
        cpu_t0 = resource.getrusage(resource.RUSAGE_SELF).ru_utime
        out = func()
        t1 = time.perf_counter()
        cpu_t1 = resource.getrusage(resource.RUSAGE_SELF).ru_utime
        result.times_ms.append((t1 - t0) * 1000)
        if "cpu_ms" not in result.extra:
            result.extra["cpu_ms"] = 0.0
        result.extra["cpu_ms"] += (cpu_t1 - cpu_t0) * 1000
        if isinstance(out, tuple) and isinstance(out[1], dict):
            result.extra.update(out[1])
    return result
