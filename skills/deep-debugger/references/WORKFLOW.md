# Deep Debugger Workflow — Chi tiết từng bước

## Bước 2: Thu thập context — checklist

| Item | Lệnh | Mục đích |
|------|------|----------|
| Stack trace đầy đủ | copy từ log, KHÔNG tóm tắt | Xác định call chain |
| Git history gần | `git log -p -5 -- <file>` | Tìm commit giới thiệu bug |
| Environment | `python --version`, `uname -a`, config | Loại trừ môi trường |
| Log quanh lỗi | `grep -B20 -A20 ERROR app.log` | Context trước/sau lỗi |

## Bước 3: Bảng giả thuyết

Mỗi giả thuyết ghi: mô tả, evidence ủng hộ, evidence phản bác, cách kiểm chứng, xác suất ban đầu.
Ví dụ thật: lỗi `KeyError: 'user'` sau commit refactor:
- H1: field bị rename trong migration (prob 60%) → check migration file
- H2: cache trả data cũ schema (prob 30%) → clear cache, rerun
- H3: API ngoài trả format khác (prob 10%) → inspect response raw

## Bước 5: Reproducer criteria

Reproducer đạt chuẩn khi: (a) chạy độc lập không cần setup đầy đủ, (b) fail 100% lần chạy, (c) nhỏ nhất có thể (≤50 dòng khuyến nghị).

