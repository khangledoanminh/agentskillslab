# Đóng góp cho AgentSkillsLab

Cảm ơn bạn quan tâm đến việc đóng góp. Project này đặt chất lượng lên số lượng: **một skill sâu tốt hơn mười skill mỏng**, và mọi thay đổi phải đi kèm bằng chứng kiểm thử — không phải lời hứa.

## Quy trình đóng góp

Fork repository, tạo branch đặt tên theo dạng `feature/<ten-skill>` hoặc `fix/<mo-ta-ngan>`, thực hiện thay đổi, chạy toàn bộ kiểm tra ở phần dưới, rồi mở pull request kèm mô tả rõ thay đổi làm gì và tại sao. PR thêm skill mới sẽ được review theo checklist "Tiêu chuẩn skill mới" bên dưới; PR thiếu test hoặc thiếu ví dụ chạy được sẽ không được merge.

## Tiêu chuẩn skill mới

Skill mới bắt buộc đáp ứng toàn bộ checklist trong `spec/SKILL_SPEC.md`. Tóm tắt tối thiểu: `SKILL.md` với frontmatter chuẩn (name, description, version, compatibility, permissions, determinism, tags); `skill.yaml` manifest đầy đủ; `scripts/` chứa công cụ deterministic chạy thật bằng thư viện chuẩn Python (không dependency bên ngoài trừ khi bắt buộc — khi đó khai báo trong `requirements.txt`); `tests/` có test script chạy trên fixture và assert kết quả thật; `examples/` có ít nhất một shell script chạy end-to-end; `references/` cho tài liệu tra cứu; `benchmarks/` đo thời gian thật. Nếu skill dùng shell command, phải có `SECURITY-ALLOW.md` justify từng vị trí file:line.

Tuyệt đối không đưa vào skill: prompt injection hay chỉ thị vượt quyền trong SKILL.md, secret thật trong bất kỳ file nào (fixture phải dùng giá trị giả dạng chuẩn như `AKIAIOSFODNN7EXAMPLE`), lệnh phá hoại trong denylist của `lib/runner.py`, hoặc dependency ngoài mà không khai báo.

## Chạy kiểm tra trước khi提交 PR

```bash
# Style: ruff 0 error
ruff check .

# Platform tests: 25/25 PASS
python3 tests/test_lib.py

# Validate toàn bộ skill
for s in skills/*/; do python3 cli/agent_skills.py validate "$s" || exit 1; done

# Test từng skill
for s in skills/*/; do python3 "$s/tests/test_core.py" || exit 1; done

# Benchmark
python3 scripts/bench_all.py
```

## Báo cáo vấn đề

Bug và lỗ hổng bảo mật được báo theo hai kênh khác nhau: bug thông thường qua issue với template mô tả hành vi kỳ vọng/thực tế; lỗ hổng bảo mật theo quy trình trong `SECURITY.md` (không mở issue công khai). Khi báo lỗi validator, hãy đính kèm fixture tái hiện để team có thể thêm vào bộ fuzzing.

## Phong cách code

Python 3.11+, thư viện chuẩn là mặc định; line length 130 ký tự; docstring tiếng Việt hoặc tiếng Anh nhất quán trong từng module; thông báo lỗi của CLI ngắn gọn và in ra stderr; JSON output của scripts luôn human-readable (indent 2) kèm trường exit rõ ràng.
