# Security Policy

AgentSkillsLab cung cấp hai lớp bảo mật: **an toàn cho người dùng** (skill không dạy agent làm việc nguy hiểm) và **an toàn khi thực thi** (script của skill không phá hoại máy). Tài liệu này mô tả cơ chế, cách báo cáo lỗ hổng và phiên bản được hỗ trợ.

## Cơ chế bảo mật của project

**Scan rules (SEC-001..006).** Validator quét toàn bộ scripts/, skill.yaml và body SKILL.md của mỗi skill theo 6 nhóm rule: phát hiện bí mật nhúng (AWS, GCP, Stripe, GitHub, Slack...), thực thi shell, eval/exec, lệnh đặc quyền (sudo, rm -rf), pickle/tempfile không an toàn, và prompt injection trong tài liệu. Finding mức HIGH/CRITICAL khiến skill **không qua validate** trừ khi được justify tường minh trong `SECURITY-ALLOW.md` kèm file:line và lý do — cơ chế này buộc mọi shell command hợp pháp phải được review và document, không thể lén đưa vào.

**Runtime envelope (lib/runner.py).** Khi agent chạy script skill qua runner: danh sách lệnh bị cấm tuyệt đối (xóa toàn bộ ổ đĩa, format, ghi đè device, pipe-to-shell từ mạng...), timeout bắt buộc, biến môi trường nhạy cảm không được truyền vào subprocess, và mọi command truyền qua subprocess dưới dạng list argument — không bao giờ `shell=True`, loại bỏ lớp command injection cơ bản.

**Permission declaration.** Mỗi skill khai báo `permissions` trong skill.yaml (filesystem, network, subprocess, install_packages, max runtime). Validator kiểm tính nhất quán giữa khai báo và code thực tế; agent nên từ chối skill có hành vi vượt khai báo.

**Fixture fuzzing.** 25 fixture test (17 malformed + 8 malicious) được chạy trong CI và audit trước mỗi release, bao gồm các tấn công prompt injection, path traversal, secret embedding và dependency confusion.

## Bản phát hành được hỗ trợ

| Phiên bản | Hỗ trợ bảo mật |
|---|---|
| 1.0.x | Đang hỗ trợ |
| < 1.0 | Không hỗ trợ |

## Báo cáo lỗ hổng

Nếu bạn tìm thấy lỗ hổng bảo mật trong platform hoặc trong một skill, vui lòng **không** mở issue công khai. Gửi mô tả (kèm cách tái hiện nếu có) tới đội duy trì qua kênh riêng của project. Đội ngũ sẽ phản hồi xác nhận trong vòng 72 giờ làm việc và công bố fix kèm bản vá trong phiên bản tiếp theo.

Lỗ hổng nghiêm trọng (remote code execution qua skill, bypass validator cho malicious skill, leak credential qua runner) sẽ được ưu tiên xử lý ngay.

## Khuyến nghị khi sử dụng

Người dùng nên luôn chạy `agent-skills validate` và `agent-skills test` trên skill tải về từ nguồn ngoài trước khi đưa vào workflow thật, đọc nội dung scripts/ trước khi cho agent thực thi, và không cấp quyền network/install cho skill không cần chúng.
