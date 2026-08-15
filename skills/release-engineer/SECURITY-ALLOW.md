# SECURITY-ALLOW.md — release-engineer

Các pattern SEC được justify explicit. Validator hạ các finding này
từ error xuống warning khi dòng/file khớp danh sách dưới.

Định dạng: `- <rule_id> <file>:<line> <lý do>`

- SEC-002-shell-exec scripts/release_check.py:23 subprocess.run([..], shell=False) — command không ghép string, args dạng list
- SEC-002-shell-exec scripts/release_check.py:34 subprocess.run([..], shell=False) — command không ghép string, args dạng list
- SEC-002-shell-exec scripts/release_check.py:97 subprocess.run([..], shell=False) — command không ghép string, args dạng list
- SEC-002-shell-exec scripts/* subprocess.run([..], shell=False) — command không ghép string, args dạng list
