# Mutation Testing Reference

## Nguyên lý

Mutant = thay đổi nhỏ code (toán tử, hằng số, điều kiện). Test suite mạnh phải làm test FAIL khi có mutant → "kill". Mutant sống sót (survive) = test suite KHÔNG phát hiện thay đổi đó → blind spot.

## Operators phổ biến

| Operator | Thay đổi | Ví dụ |
|----------|----------|-------|
| AOR | `+` → `-`, `*` → `/` | `a + b` → `a - b` |
| ROR | `>` → `>=`, `==` → `!=` | `if x > 0` → `if x >= 0` |
| UOI | `i++` → `i--` | vòng lặp |
| LCR | `&&` → `or` | `a and b` → `a or b` |
| SDL | xóa statement | xóa dòng assign |

## Metric

mutation score = killed / total (không tính equivalent mutants). Target ≥ 70%.
Equivalent mutant (code thay đổi nhưng behavior giữ nguyên) phải mark manual, không count.

