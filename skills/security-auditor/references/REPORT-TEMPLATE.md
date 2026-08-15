# Security Audit Report — Template

## Summary
- Repo: {repo}
- Ngày audit: {date}
- Files quét: {n} | Findings: {n} (CRITICAL {n}, HIGH {n}, MEDIUM {n}, LOW {n}, INFO {n})
- Not scanned: {danh sách nhóm rule không quét được + lý do}

## Confirmed Findings
| # | Severity | Rule | File:Line | Evidence (snipped) | Xác nhận | Khuyến nghị |
|---|----------|------|-----------|--------------------|----------|-------------|
| 1 | ... | | | | TRUE/FALSE/ADJUSTED | |

## False Positives
Giải thích từng finding bị loại và lý do (VD: dummy secret trong test fixture).

## Recommendations (ưu tiên)
1. CRITICAL trước, mỗi khuyến nghị kèm ví dụ code an toàn.

## Limitations
Scanner pattern-based không thay thế pentest; chỉ quét file text; binary không quét.
