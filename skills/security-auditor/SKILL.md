---
name: security-auditor
description: "Audit a repository for security issues: secrets, dangerous APIs, unsafe shell commands, insecure configs, and suspicious patterns, then produce an evidence-based severity-rated findings report. Use when the user asks to audit, scan, or review a repo for security vulnerabilities or risks."
---

# Security Auditor

Audit repository code với sự kết hợp giữa **scanner determinist** (scripts) và **phân tích của AI**. Scanner chạy thật, tìm pattern thật; AI xếp hạng severity, loại trừ false positive và viết báo cáo. Tuyệt đối không invent findings — nếu không quét được, trả về trạng thái `not_scanned`.

## Quy trình (6 bước)

1. **Chuẩn bị**: xác định root repo cần audit. Chạy `scripts/audit.py` với root dir.
2. **Review output JSON**: mỗi finding có `rule_id`, `severity`, `file`, `line`, `evidence`, `why`.
3. **Phân tích từng finding** (bước AI): xác nhận thật/dương tính giả, nâng/hạ severity dựa trên ngữ cảnh (VD: secret trong test fixture dummy → hạ xuống INFO).
4. **Bổ sung phân tích kiến trúc** (AI, optional): coupling permission, trust boundary, nơi input không tin cậy vào hệ thống.
5. **Viết báo cáo** `security-report.md`: bảng findings đã xác nhận + khuyến nghị fix ưu tiên theo severity.
6. **Verify không leak**: báo cáo chỉ chứa evidence đã snip; không copy secret thật vào báo cáo.

## Severity framework

| Severity | Nghĩa | Ví dụ |
|----------|-------|-------|
| CRITICAL | Exploitable ngay, mất credential/control | Secret thật trong source, RCE path |
| HIGH | Nguy hiểm cao, cần context để khai thác | Dangerous API với input user, curl\|sh |
| MEDIUM | Risk có điều kiện | Unsafe deserialization nội bộ, config yếu |
| LOW | Best-practice violation | Hardcoded URL nội bộ, comment chứa key cũ |
| INFO | Đáng chú ý, không phải lỗi | Dependency cũ chưa có CVE |

## Quy tắc phân tích AI

- Evidence trước, kết luận sau. Mỗi finding trong báo cáo phải tham chiếu file + line.
- Nếu scanner không chạy được (thiếu tool): ghi `not_scanned` cho nhóm rule đó, không giả danh sách rỗng.
- Dương tính giả phải được giải thích ("secret là dummy trong test fixture").
- Khuyến nghị fix cụ thể, có ví dụ code an toàn thay thế.

## Scripts

- `scripts/audit.py <repo-root> [--output findings.json]` — chạy tất cả nhóm rule SEC-001..006, output JSON.

## Referências

- [RULES.md](references/RULES.md) — chi tiết từng rule và ví dụ pattern
- [REPORT-TEMPLATE.md](references/REPORT-TEMPLATE.md) — template báo cáo chuẩn

## Examples

```bash
python3 scripts/audit.py /path/to/repo --output findings.json
# findings.json: {"scanned": 14, "findings": [...], "not_scanned": []}
```
