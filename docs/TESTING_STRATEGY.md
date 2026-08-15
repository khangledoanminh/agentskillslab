# AgentSkillsLab — Testing Strategy

**Version:** 1.0 · **Date:** August 15, 2026

## 1. Principles

Mọi claim chất lượng phải chứng minh được bằng test chạy thật: không claim "test pass" nếu không chạy, không fabricate benchmark number. Ưu tiên evidence over assertion.

## 2. Test Pyramid

| Tầng | Phạm vi | Công cụ | Coverage mục tiêu |
|------|---------|---------|-------------------|
| Unit | lib/*.py từng hàm (parser, validator rules, index, security patterns) | pytest | nhánh chính của mọi rule validation |
| Integration | CLI commands trên fixtures thật | subprocess + pytest | mọi command: validate/test/benchmark/inspect/search/doctor |
| E2E skill | Chạy scripts/ của từng flagship skill trên fixture repo | pytest | mỗi skill có ít nhất 1 happy path + 1 failure path |
| Adversarial | Malicious fixtures (typosquat, obfuscation, traversal, exhaustion) | pytest | mọi finding ID trong THREAT_MODEL có test tương ứng |
| Mutation | Test-the-tests: fix lỗi giả trong code → test phải fail | script mutation | xác minh test không yếu |

## 3. Fixtures

```
fixtures/
├── valid/              # 3 skill hợp lệ đầy đủ (minimal, standard, flagship)
├── malformed/          # thiếu SKILL.md, frontmatter hỏng, name sai pattern...
├── malicious/          # obfuscation, dangerous APIs, traversal, symlinks, huge manifest
└── repos/              # repo mẫu để skill test-engineer/security-auditor chạy trên
```

Fixtures phải không chứa secret thật (dùng dummy pattern `AKIAFAKE...`), không file thực thi nguy hiểm thật.

## 4. Skill Self-Testing

Mỗi flagship skill có `tests/` riêng kiểm thử chính scripts của nó (ví dụ `security-auditor/tests/scan_on_fixture_repo.sh` chạy scanner trên `fixtures/repos/vulnerable-sample` và assert đúng số finding mong đợi). `agent-skills test <skill>` chạy test suite đó.

## 5. Benchmarks

`benchmarks/` đo hiệu năng **thật** của CLI: validator speed trên 10/100/1000 skill, startup time, index build time. Quy tắc: mọi số liệu trong docs phải từ benchmark chạy thật, kèm environment (OS, CPU, Python version).

## 6. CI

GitHub Actions: lint (ruff), unit+integration tests, skill tests, build, advisory check. Không có secret trong CI.

## 7. Coverage & Mutation

Coverage đo bằng `pytest --cov=lib --cov=cli`; mục tiêu ≥80% statements trên lib. Mutation test thực hiện thủ công theo checklist (inject bug thật, xác nhận test fail) — kết quả trong AUDIT_SUMMARY.
