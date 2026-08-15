# Modernization Guide — what is IN scope vs OUT

## IN scope (được phép)

- Dependency version fix để build/test pass
- Security patch dependencies
- Toolchain version update nếu bắt buộc
- Doc generation từ code hiện tại
- CI skeleton (chạy test)

## OUT of scope (KHÔNG làm nếu không được yêu cầu explicit)

- Rewrite ngôn ngữ/framework
- Đổi kiến trúc
- Feature mới
- Reformat toàn repo (format chỉ file chạm tới)

## Decision log format

Mỗi decision quan trọng ghi: `DECISION: <what> — RATIONALE: <why> — ALTERNATIVES: <what else considered>`.
Decision log nằm trong `docs/decisions/` của repo được hồi sinh.

