---
name: deep-debugger
description: "Root-cause debugging workflow: reconstruct error context, build hypotheses, test each hypothesis against evidence, and prove the root cause with a reproducer. Use when debugging a failing test, crash, or confusing error message and you need to find the actual root cause rather than guess fixes."
---

# Deep Debugger

Tìm root cause thật, không đoán mò. Quy trình: **Tái hiện → Thu thập → Giả thuyết → Kiểm chứng → Chứng minh → Fix có test**.

## Quy trình (6 bước)

1. **Tái hiện lỗi**: chạy lại đúng lệnh/context lỗi được báo cáo. Nếu không tái hiện được, dừng và hỏi thêm thông tin. Không fix khi chưa tái hiện.
2. **Thu thập context**: stack trace đầy đủ, logs, environment (OS, phiên bản, config), git history gần đây (`git log -p -5`), source file liên quan.
3. **Dựng giả thuyết (≥2)**: từ evidence, liệt kê các root cause có thể, xếp theo xác suất. Ghi rõ evidence ủng hộ/phản bác từng giả thuyết.
4. **Kiểm chứng từng giả thuyết**: dùng debugger/bisect/logs để loại trừ. Mỗi lần loại trừ ghi lại lý do.
5. **Chứng minh root cause**: viết minimal reproducer — đoạn code nhỏ nhất tái hiện lỗi. Nếu reproducer fail → root cause xác nhận.
6. **Fix + regression test**: sửa tại root cause (không workaround symptom), thêm test tái hiện lỗi để đảm bảo không tái diễn.

## Nguyên tắc

- Evidence trước, kết luận sau. Không bỏ qua dòng log nào trong stack trace.
- Nếu evidence mâu thuẫn, quay lại bước 2 thay vì ép giả thuyết.
- Repro case là bằng chứng: phải kèm theo báo cáo final.
- Không bao giờ sửa nhiều chỗ cùng lúc khi chưa biết root cause.

## Scripts

- `scripts/collect_context.py <repo> [--log FILE]` — trích stack trace, git history 5 commit gần, file list có sửa gần đây.
- `scripts/hypothesis.md` — template bảng giả thuyết (AI điền).

## References

- [WORKFLOW.md](references/WORKFLOW.md) — chi tiết từng bước với ví dụ thật
- [HYPOTHESIS-TEMPLATE.md](references/HYPOTHESIS-TEMPLATE.md) — template bảng giả thuyết
