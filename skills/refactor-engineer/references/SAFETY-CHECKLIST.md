# Refactor Safety Checklist

Trước khi refactor:
- [ ] Regression suite chạy và GREEN
- [ ] Characterization test viết cho behavior quan trọng (nếu chưa có test)
- [ ] Đã commit trạng thái hiện tại

Trong khi refactor:
- [ ] Mỗi bước nhỏ (≤ 1 smell, ≤ 50 dòng thay đổi)
- [ ] Regression chạy sau MỖI bước
- [ ] Commit riêng từng bước với message mô tả

Sau khi refactor:
- [ ] Regression suite GREEN
- [ ] Behavior entry points không đổi (verify output)
- [ ] Smell detector re-run: smell giảm
- [ ] Không có smell MỚI sinh ra

