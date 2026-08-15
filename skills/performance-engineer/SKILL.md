---
name: performance-engineer
description: "Evidence-based performance optimization: benchmark the real code before and after changes, profile to find the true bottleneck, patch, and verify improvement with statistical rigor. Use when code is slow, latency needs reducing, or optimization claims must be proven."
---

# Performance Engineer

Tối ưu dựa trên số liệu THẬT, không dựa trên cảm giác. Pipeline: **benchmark trước → profile → xác định bottleneck → patch → benchmark lại → so sánh thống kê**.

## Quy trình (6 bước)

1. **Benchmark baseline**: chạy code thật nhiều lần (≥5 iterations), lấy median + p95. Ghi environment (OS, Python, CPU). Không dùng 1 lần đo.
2. **Profile**: dùng cProfile/timeit/line_profiler trên workload thật. Xác định top-3 hàm tốn thời gian nhất.
3. **Identify bottleneck**: chọn 1 bottleneck lớn nhất có evidence rõ (phần trăm thời gian). KHÔNG tối ưu nhiều chỗ cùng lúc.
4. **Patch**: sửa tối thiểu tại bottleneck. Ghi rõ giả thuyết cải thiện.
5. **Benchmark again**: cùng workload, cùng environment, ≥5 iterations. Tính speedup = median_before / median_after.
6. **Verify**: speedup ≥20% mới coi là significant; kiểm tra correctness (output không đổi); kiểm tra không phá trade-off (memory, readability).

## Nguyên tắc

- Median, không mean (chống outlier).
- Warmup trước khi đo.
- Một thay đổi một lần — isolate variable.
- Không optimze premature: chỉ tối ưu khi có số liệu chậm thật.
- Nếu patch làm chậm: revert, ghi lại learning.

## Scripts

- `scripts/profile_code.py <target> [--iterations N]` — wrapper cProfile + timing median.
- `scripts/compare.py before.json after.json` — so 2 kết quả benchmark, tính speedup + verdict.

## References

- [PROFILING-TOOLS.md](references/PROFILING-TOOLS.md)
- [STATS-NOTES.md](references/STATS-NOTES.md) — tại sao median, outlier handling
