# SECURITY-ALLOW.md — test-engineer

Các pattern SEC được justify explicit. Validator hạ các finding này
từ error xuống warning khi dòng/file khớp danh sách dưới.

Định dạng: `- <rule_id> <file>:<line> <lý do>`

- SEC-002-shell-exec scripts/coverage_report.py:32 subprocess.run([..], shell=False) — command không ghép string, args dạng list
- SEC-002-shell-exec scripts/coverage_report.py:66 subprocess.run([..], shell=False) — command không ghép string, args dạng list
- SEC-002-shell-exec scripts/mutate.py:80 subprocess.run([..], shell=False) — command không ghép string, args dạng list
- SEC-002-shell-exec scripts/* subprocess.run([..], shell=False) — command không ghép string, args dạng list
