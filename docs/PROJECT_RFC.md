# AgentSkillsLab — Project RFC

**Status:** Draft → Accepted
**Authors:** AgentSkillsLab Maintainers (Manus AI)
**Date:** August 15, 2026
**Version:** 1.0

---

## 1. Abstract

AgentSkillsLab (ASL) là một hệ sinh thái open-source các **AI Agent Skills** cấp production, trong đó mỗi Skill không chỉ là một tệp hướng dẫn (SKILL.md) mà là một **mini developer tool** hoàn chỉnh: có manifest metadata, scripts thực thi được, bộ test riêng, fixtures, benchmarks, tài liệu tham chiếu và khai báo permissions. Bên trên hệ sinh thái Skill, ASL cung cấp một CLI (`agent-skills`) để validate, test, benchmark và quản lý Skills theo một **Skill Specification** chính thức.

Triết lý trung tâm:

> Whenever a task can be handled deterministically by a real tool, prefer a real tool over asking an LLM to hallucinate the result.

## 2. Problem Statement

Hệ sinh thái Agent Skills hiện nay (định dạng mở của Anthropic, được Claude Code, VS Code, OpenCode, Cursor, Kilo, Codex hỗ trợ) giải quyết vấn đề **khám phá và truyền tải tri thức** cho coding agents, nhưng có ba lỗ hổng cấu trúc:

1. **Không có chuẩn kiểm soát chất lượng.** Toàn bộ spec chỉ yêu cầu `name` và `description` trong YAML frontmatter. Kết quả là phần lớn Skills trong cộng đồng chỉ là "prompt collection" — không có test, không có benchmark, không có cách nào xác minh Skill hoạt động đúng.
2. **Không có mô hình bảo mật.** Anthropic tự khuyến nghị "install skills only from trusted sources" nhưng không cung cấp cơ chế: không có permission boundaries, không có schema validation, không có threat model cho Skills từ nguồn bên thứ ba.
3. **Không có tooling vận hành.** Không tồn tại validator, test harness hay registry local nào cho format này. Developer không thể trả lời câu hỏi "Skill này có an toàn và đáng tin không?" bằng công cụ, chỉ bằng niềm tin.

## 3. Vision

> "npm/cargo + a quality standard + security tooling + testing infrastructure for AI Agent Skills."

Project phải **hữu dụng ngay cả khi không có LLM API**: các script, validator, test harness, benchmark framework hoạt động hoàn toàn deterministically. AI enhances the Skills, không required cho deterministic functionality.

## 4. Goals

| # | Goal | Metric |
|---|------|--------|
| G1 | Định nghĩa Skill Specification v1.0 | SKILL_SPEC.md, schema JSON |
| G2 | CLI `agent-skills` hoàn chỉnh | validate/test/benchmark/inspect/search/doctor |
| G3 | 10 flagship Skills production-grade | Mỗi skill: scripts + tests + examples + benchmarks |
| G4 | Bộ test suite cho chính project | ≥ 100 test cases, pass rate 100% |
| G5 | Threat model + permission boundaries | THREAT_MODEL.md, kiểm thử adversarial |
| G6 | Khả dụng đa agent | Mỗi skill compatible với Claude Code, Codex, Cursor, Copilot, OpenCode, Kilo |

## 5. Non-Goals (deliberately rejected)

| Rejected | Lý do |
|----------|-------|
| MCP server | Skill là artifact độc lập; MCP thêm runtime coupling không cần thiết cho spec |
| Registry công khai | "Do not implement a registry prematurely" — local-first, format phải xuất sắc trước |
| Khóa vào một agent (Claude-only) | Vendor-neutral; frontmatter Anthropic-compatible nhưng metadata mở rộng trong skill.yaml |
| Tự động "fix" code trong repo người dùng | Các skill refactor/resurrection luôn yêu cầu approval, không destructive mặc định |
| Thêm AI API calls vào validator | Validator 100% deterministic; AI là optional layer |

## 6. Proposed Architecture (summary)

```
agentskillslab/
├── cli/                    # Python CLI `agent-skills` (zero-dep: stdlib + yaml)
├── spec/                   # SKILL_SPEC.md + JSON schema
├── skills/                 # 10 flagship skills
├── lib/                    # shared Python library (validator, runner, security)
├── tests/                  # project-level tests
├── fixtures/               # shared fixtures
├── benchmarks/             # project benchmarks
├── docs/                   # RFC, ARCHITECTURE, THREAT_MODEL, ROADMAP...
└── SECURITY.md, CONTRIBUTING.md, CHANGELOG.md, LICENSE
```

Chi tiết xem `docs/ARCHITECTURE.md` và `docs/SKILL_SPEC.md`.

## 7. Flagship Skills (v1)

Bốn skill đầu được chọn làm foundation vì chúng chứng minh được cả **deterministic tooling + AI workflow** và tạo dependency tự nhiên cho các skill sau:

1. **security-auditor** — scanner determinist (secrets, dangerous APIs, shell commands, config) + AI phân tích findings. Tạo nền cho mọi skill khác.
2. **deep-debugger** — workflow evidence-based: thu thập → hypothesis → loại trừ → root cause → minimal fix.
3. **test-engineer** — inspect coverage → generate tests → run → mutate → measure → improve.
4. **dependency-doctor** — scanner npm/pip/cargo/go/gradle: outdated, vulnerable, unused, conflicts, license.

Bốn skill mở rộng:

5. **performance-engineer** — benchmark before/profile/patch/again với số liệu thật.
6. **refactor-engineer** — phát hiện code smells (God class, long function, duplication, circular dep) + regression tests.
7. **codebase-architect** — phân tích architecture: modules, coupling, hotspots, diagrams.
8. **repo-resurrection** — workflow khôi phục repo abandoned (demo giá trị cao nhất).

Hai skill bổ trợ:

9. **release-engineer** — versioning, changelog, artifacts, checksums.
10. **documentation-engineer** — tạo/maintain docs tự repo (không tạo nội dung sai sự thật).

## 8. Security Posture

Coi mọi Skill bên thứ ba là **untrusted**. Threat model đầy đủ trong `docs/THREAT_MODEL.md` bao quát: malicious scripts, prompt injection, credential theft, data exfiltration, arbitrary command execution, typosquatting, obfuscated code, malicious downloads, resource exhaustion. Permission boundaries và chế độ safe execution được kiểm thử adversarial trước khi release.

## 9. Phased Implementation

| Phase | Nội dung | Exit criteria |
|-------|----------|---------------|
| 0 | Research + RFC + Architecture | RFC accepted |
| 1 | Spec + validator + minimal runtime | `agent-skills validate` hoạt động trên fixtures |
| 2 | Testing/fixtures/benchmark infrastructure | 100% test pass trên harness |
| 3 | 4 skill foundation | 4 skills validated + tested |
| 4 | 4 skill mở rộng + 2 bổ trợ | 10 skills validated + tested |
| 5 | Security hardening | Adversarial tests pass |
| 6 | CLI polish + search/inspect/doctor | CLI audit pass |
| 7 | Documentation + examples chạy được | doc audit pass |
| 8 | Cross-agent compatibility | Compatibility matrix verified |
| 9 | Release engineering | Release artifacts reproducible |

## 10. Open Questions

1. Có nên thêm trường `cost_estimate` (token budget) vào skill.yaml? → **Reject v1**: description đủ để trigger; thêm sau khi có dữ liệu sử dụng thật.
2. Format metadata: YAML vs TOML? → **Chọn YAML**: thống nhất với frontmatter SKILL.md, giảm công cụ parsing.
3. Dependency graph giữa các skills (refactor-engineer cần test-engineer)? → **Chấp nhận** khai báo `requires` trong skill.yaml; runtime cảnh báo, không tự cài.

## 11. References

1. Anthropic — [Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
2. Anthropic Engineering — [Equipping agents for the real world](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
3. agentskills.io — Agent Skills open standard
4. anthropics/skills — [Official skills repository](https://github.com/anthropics/skills)
5. Microsoft — [Agent Skills documentation](https://learn.microsoft.com/en-us/agent-framework/agents/skills)
6. VS Code — [Use Agent Skills in VS Code](https://code.visualstudio.com/docs/agent-customization/agent-skills)
