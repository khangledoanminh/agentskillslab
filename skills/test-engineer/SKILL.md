---
name: test-engineer
description: "Coverage-driven test engineering: analyze code, find uncovered paths, generate tests targeting them, run, measure coverage, mutate to verify test strength, and iterate until quality targets are met. Use when asked to write tests, improve test coverage, or verify that existing tests actually catch bugs."
---

# Test Engineer

Viết test có mục tiêu, không viết test cho đủ số. Vòng lặp: **inspect → uncovered paths → generate → run → coverage → mutate → improve → dừng khi đạt target**.

## Quy trình (7 bước)

1. **Inspect code**: đọc module, xác định hàm public, branches, edge cases, error paths.
2. **Tìm uncovered paths**: chạy coverage tool (`python3 -m pytest --cov`) để lấy coverage report thật. KHÔNG đoán coverage bằng mắt.
3. **Generate tests**: ưu tiên branch chưa cover, edge cases (empty, None, boundary, error paths). Mỗi test có tên mô tả hành vi + assert cụ thể.
4. **Run**: chạy toàn bộ suite, mọi test phải pass.
5. **Measure coverage**: lấy line + branch coverage thật từ tool. Ghi số trước/sau.
6. **Mutate** (nếu mutation tool có): chạy mutant (VD thay `+` thành `-`, đổi điều kiện). Test mạnh phải kill mutant. Tỉ lệ survive cao = test yếu dù coverage cao.
7. **Improve**: dựa vào mutant survive + branch miss, viết thêm test. Lặp 3–7 cho tới: coverage mục tiêu (VD ≥80%) VÀ mutant kill rate ≥70%.

## Quality targets mặc định

| Metric | Target |
|--------|--------|
| Line coverage | ≥ 80% |
| Branch coverage | ≥ 70% |
| Mutation kill rate | ≥ 70% |
| Flaky tests | 0 (chạy 3 lần phải nhất quán) |

## Nguyên tắc

- Test hành vi, không test implementation detail (trừ khi cố ý contract test).
- Test phải deterministic; không dùng sleep/rand mà không seed.
- Coverage 100% không phải mục tiêu — diminishing returns; dừng khi đạt target + chi phí hợp lý.
- Test file đặt cạnh code hoặc trong tests/, tên rõ ràng.

## Scripts

- `scripts/coverage_report.py <module-dir> [--target N]` — chạy pytest --cov, xuất JSON coverage thật.
- `scripts/mutate.py <module> [--operator list]` — simple mutator: thay arithmetic/condition operators, chạy test, báo mutant survive/kill.

## References

- [COVERAGE-GUIDE.md](references/COVERAGE-GUIDE.md)
- [MUTATION-REFERENCE.md](references/MUTATION-REFERENCE.md)
