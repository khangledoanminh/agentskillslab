# SECURITY-ALLOW.md — deep-debugger

Các pattern SEC được justify explicit. Validator hạ các finding này
từ error xuống warning khi dòng/file khớp danh sách dưới.

Định dạng: `- <rule_id> <file>:<line> <lý do>`

- SEC-002-shell-exec scripts/collect_context.py:22 subprocess.run([..], shell=False) — command không ghép string, args dạng list
- SEC-002-shell-exec scripts/collect_context.py:50 subprocess.run([..], shell=False) — command không ghép string, args dạng list
- SEC-002-shell-exec scripts/* subprocess.run([..], shell=False) — command không ghép string, args dạng list
