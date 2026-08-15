# AgentSkillsLab — Roadmap

**Version:** 1.0 · **Date:** August 15, 2026

## v1.0 — Foundation (hiện tại)

| Milestone | Deliverables | Trạng thái |
|-----------|--------------|-----------|
| M0 | PROJECT_RFC, ARCHITECTURE, THREAT_MODEL, SKILL_SPEC | ✓ |
| M1 | Spec + JSON schema + validator + runner + CLI core | ✓ |
| M2 | Test harness, fixtures (valid/malformed/malicious) | ✓ |
| M3 | 4 skill foundation (security-auditor, deep-debugger, test-engineer, dependency-doctor) | ✓ |
| M4 | 6 skill còn lại (performance-engineer, refactor-engineer, codebase-architect, repo-resurrection, release-engineer, documentation-engineer) | ✓ |
| M5 | Security hardening + adversarial tests | ✓ |
| M6 | CLI đầy đủ (validate/test/benchmark/inspect/search/doctor) | ✓ |
| M7 | Docs + examples chạy được + compatibility matrix | ✓ |
| M8 | Audit toàn diện + AUDIT_SUMMARY + release | ✓ |

## v1.1 — Candidate

Permission envelope hardening (seccomp option trên Linux), execution-backend container, parallel validation, `agent-skills publish` (dry-run đóng gói artifact có checksum), compatibility với Windows (kiểm chứng thực tế).

## v2.0 — Horizon

Skill registry protocol (manifest index có signature), skill dependency resolver, đánh giá tự động chất lượng skill (quality score), integration với CI (GitHub Action `agentskillslab/validate-action`).

## Out of Scope (forever)

Registry public hosted bởi ASL team (quản trị trust quá lớn cho maintainer nhỏ); MCP server; vendor lock-in.
