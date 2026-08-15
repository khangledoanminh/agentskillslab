# SECURITY-ALLOW.md — repo-resurrection

Các pattern SEC được justify explicit. Validator hạ các finding này
từ error xuống warning khi dòng/file khớp danh sách dưới.

Định dạng: `- <rule_id> <file>:<line> <lý do>`

- SEC-002-shell-exec scripts/audit_state.py:28 subprocess.run([..], shell=False) — command không ghép string, args dạng list
- SEC-002-shell-exec scripts/* subprocess.run([..], shell=False) — command không ghép string, args dạng list
