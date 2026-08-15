---
name: documentation-engineer
description: "Assess and repair documentation quality with measurable checks: missing docstrings, undocumented public APIs, dead links, stale examples, and readability scoring, then generate documentation that matches the current code exactly. Use when docs are missing, outdated, or an onboarding guide is needed."
---

# Documentation Engineer

Docs phải khớp code THẬT tại thời điểm viết. Pipeline: **audit coverage thật → tìm lỗ hổng → viết từ source code hiện tại → verify links + examples chạy được**.

## Quy trình (5 bước)

1. **Audit coverage**: chạy `scripts/doc_coverage.py <repo>` — % public functions/classes có docstring, % modules có README, dead links trong markdown.
2. **Prioritize gaps**: public API không có doc > nội bộ > ví dụ cũ. Ưu tiên API public trước.
3. **Generate docs từ code thật**: parse signature + docstring hiện có + source body; viết docs mô tả đúng behavior hiện tại. KHÔNG extrapolate tính năng chưa có trong code.
4. **Verify examples**: mỗi code example trong docs phải chạy được (script chạy example, kiểm exit code).
5. **Verify links**: scan mọi link trong docs → target tồn tại (file local phải tồn tại; URL external đánh dấu cần manual verify).

## Metrics mặc định

| Metric | Target |
|--------|--------|
| Public API doc coverage | ≥ 90% |
| Dead internal links | 0 |
| Runnable examples | 100% ví dụ có code block |

## Nguyên tắc

- Docs mô tả behavior hiện tại; nếu code sai, báo bug riêng — không viết docs theo ý muốn.
- Ví dụ phải chạy; ví dụ không chạy worse hơn không có ví dụ.
- Markdown nhất quán: heading levels, code fence language.

## Scripts

- `scripts/doc_coverage.py <repo> [--output report.json]`
- `scripts/check_examples.py <docs-dir>` — chạy code blocks trong markdown

## References

- [STYLE-GUIDE.md](references/STYLE-GUIDE.md)
- [EXAMPLE-RULES.md](references/EXAMPLE-RULES.md)
