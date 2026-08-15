# Security Rules Reference

| Rule | Nhóm | Severity mặc định | Pattern | Ví dụ dương tính |
|------|------|-------------------|---------|------------------|
| SEC-001-aws-key | Secrets | CRITICAL | `\bAKIA[0-9A-Z]{16}\b` | `AKIAFAKEEXAMPLE12345` |
| SEC-001-generic-key | Secrets | CRITICAL | api_key/secret_key assignment ≥16 chars | `api_key = "abc...123"` |
| SEC-001-private-key | Secrets | CRITICAL | `-----BEGIN ... PRIVATE KEY` | Embedded PEM key |
| SEC-001-bearer-token | Secrets | CRITICAL | bearer + token ≥20 chars | `Authorization: Bearer eyJ...` |
| SEC-001-password-literal | Secrets | CRITICAL | password = "..." | `password = "hunter2"` |
| SEC-002-shell-exec | Dangerous API | HIGH | os.system, subprocess.* | `os.system(cmd)` |
| SEC-002-eval-exec | Dangerous API | HIGH | eval(, exec( | `eval(user_input)` |
| SEC-002-pickle | Dangerous API | HIGH | pickle.loads, yaml.load không Loader | `pickle.loads(data)` |
| SEC-002-tempfile-insecure | Dangerous API | MEDIUM | tempfile.mktemp | Race condition risk |
| SEC-002-hardcoded-url | Dangerous API | LOW | http(s):// dài | Endpoint nội bộ |
| SEC-003-rm-rf | Shell | HIGH | rm -rf hướng root/biến | `rm -rf $DIR/*` |
| SEC-003-curl-exec | Shell | HIGH | curl/wget pipe vào sh | `curl url \| bash` |
| SEC-003-sudo | Shell | MEDIUM | sudo lệnh side-effect | `sudo rm ...` |
| SEC-003-chmod-recursive | Shell | MEDIUM | chmod -R 777 | Quyền quá rộng |
| SEC-004-base64-exec | Obfuscation | CRITICAL | base64 -d pipe sh | Che giấu payload |
| SEC-004-hex-exec | Obfuscation | CRITICAL | chuỗi \x dài | Code ẩn |
| SEC-004-rot13-tr | Obfuscation | CRITICAL | tr xoay chuỗi dài | Che giấu nội dung |
| SEC-004-heredoc-exec | Obfuscation | CRITICAL | heredoc pipe sh | Che giấu payload |
| SEC-005-* | Prompt injection | HIGH | ignore previous instructions, role escalation, data exfil instruction | Trong SKILL.md |
| SEC-006-path-join-external | Traversal | MEDIUM | Path join với .. | `os.path.join(root, user, '..')` |
