# Release Checklist Reference

| # | Item | Check cách | Evidence |
|---|------|------------|----------|
| 1 | CHANGELOG entry version mới | grep CHANGELOG "## [<version>]" | line match |
| 2 | Version bump nhất quán | metadata == git tag == CHANGELOG | 3 giá trị bằng nhau |
| 3 | Tests pass | chạy test suite repo | exit 0 + count |
| 4 | Build artifact tạo được | `python3 -m build` / `npm pack` | file tồn tại |
| 5 | LICENSE tồn tại | file check | tồn tại |
| 6 | Artifact không chứa file nhạy cảm | secret scan artifact | 0 match |
| 7 | Binary không trong source dist | list artifact contents | không có .so/.exe |
| 8 | README đề cập version mới | grep | line match |

Item nào không áp dụng được (VD: repo chưa có CI) ghi `NA` với lý do, KHÔNG bỏ qua silent.

