---
name: refactor-engineer
description: Detect code smells (God class, long functions, duplication, circular dependencies, bad abstractions) with real static analysis, refactor safely with regression tests as guardrails, and verify no behavior change. Use when improving code structure, reducing technical debt, or preparing legacy code for extension.
---

# Refactor Engineer

Refactor an toàn = **phát hiện thật + regression guard + verify behavior không đổi**. Không refactor vì thích — refactor vì có smell cụ thể và risk được kiểm soát.

## Quy trình (6 bước)

1. **Phát hiện smells** (script thật): chạy `scripts/detect_smells.py <repo>` — tìm God class (>500 dòng, >15 method), long function (>50 dòng, >4 nested), duplication (clone detection qua normalized hashing), circular dependency (import graph), bad abstraction (deep inheritance, shotgun surgery indicators).
2. **Chọn mục tiêu**: 1 smell, ưu tiên theo: frequency × sửa dễ × impact. Không refactor toàn repo cùng lúc.
3. **Establish guardrails**: chạy regression test suite hiện có (hoặc viết characterization test nếu chưa có) — green trước khi chạm code.
4. **Refactor từng bước nhỏ**: mỗi bước giữ behavior, chạy regression sau mỗi bước. Commit riêng từng bước.
5. **Verify**: regression suite green + diff behavior kiểm tra (output các entry point không đổi) + re-run smell detector xác nhận smell giảm.
6. **Report**: bảng smell trước/sau, danh sách commits, risk còn lại.

## Nguyên tắc

- Behavior preservation là bất biến — test fail = revert.
- Một smell một lần refactor.
- Không đổi API public nếu không cần; nếu đổi, cập nhật callers cùng lúc + doc.
- Refactor nhỏ > refactor lớn.

## Scripts

- `scripts/detect_smells.py <repo> [--thresholds FILE]` — output JSON smells với severity.
- `scripts/import_graph.py <repo>` — vẽ dependency graph, phát hiện cycle.

## References

- [SMELL-CATALOG.md](references/SMELL-CATALOG.md) — định nghĩa + ngưỡng từng smell
- [SAFETY-CHECKLIST.md](references/SAFETY-CHECKLIST.md)
