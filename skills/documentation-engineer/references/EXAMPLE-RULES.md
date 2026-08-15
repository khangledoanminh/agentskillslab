# Runnable Example Rules

1. Mọi code block dạng instruction (không phải illustration) phải chạy được khi copy-paste.
2. Example bao gồm: setup (nếu cần), action, expected output comment.
3. Nếu example cần fixture: script tạo fixture inline hoặc trỏ fixture có sẵn trong repo.
4. Example không dùng placeholder cần thay thế ([YOUR_TOKEN]) trừ khi docs dạy cấu hình — khi đó ghi rõ bắt buộc thay.
5. Verify: `scripts/check_examples.py` chạy mọi code block, exit code 0 = pass.
6. Example cũ hơn code = example sai: khi code đổi behavior, example phải update cùng commit.

