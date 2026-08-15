# Research Notes — Agent Skills Ecosystem (Aug 2026)

## Official spec
- Agent Skills là chuẩn mở của Anthropic: https://agentskills.io/ — một thư mục chứa SKILL.md với YAML frontmatter (name + description bắt buộc).
- name: ≤64 chars, lowercase + numbers + hyphens, không chứa reserved words ("anthropic", "claude").
- Progressive disclosure 3 level: (1) metadata (frontmatter) luôn load vào system prompt; (2) body SKILL.md khi trigger; (3) files tham chiếu/scripts khi cần.
- Scripts: chạy qua bash, chỉ output vào context.

## Các sản phẩm hỗ trợ
- Claude API (skills-2025-10-02 header, sandboxed container, không network), Claude Code (~/.claude/skills, .claude/skills), claude.ai (upload zip), Claude Agent SDK, Microsoft Foundry.
- VS Code supports Agent Skills (SKILL.md + frontmatter, code.visualstudio.com/docs/agent-customization/agent-skills).
- Microsoft agent-framework/agents/skills (learn.microsoft.com) — Agent Skills là "portable packages of instructions, scripts, and resources".
- OpenCode, Cursor, Kilo, Cline (via Skills tab) cũng adopt format tương tự.

## Ecosystem hiện có
- anthropics/skills: repo chính thức, template + spec + ví dụ (Apache 2.0; docx/pdf/xlsx/pptx source-available).
- Registries: iflytek/skillhub (self-hosted registry), agentregistry.ai, TrueFoundry skills registry, upskill (10k+ skills indexed).
- Vấn đề: phần lớn skills trong cộng đồng là "prompt collection" — chỉ SKILL.md viết tốt, KHÔNG có tests, KHÔNG có validator, KHÔNG có security model.

## Gap & differentiation cho AgentSkillsLab
1. Không có chuẩn schema metadata ngoài name/description → ASL thêm skill.yaml với version, license, dependencies, compatibility, permissions.
2. Không có validator → ASL CLI `agent-skills validate` kiểm tra schema, references, scripts, security.
3. Không có security/trust model → ASL threat model + permission boundaries.
4. Không có tests/benchmarks cho skill chất lượng → ASL bắt buộc tests/ + benchmarks/ directory.
5. Không có deterministic tooling → ASL mỗi skill flagship có scripts tự chạy + AI phân tích.

## Quyết định architecture
- Python CLI `agent-skills` (zero external deps nếu có thể; pyyaml cho YAML).
- Skill format: SKILL.md (Anthropic-compatible frontmatter) + skill.yaml (metadata mở rộng ASL) + scripts/ + references/ + assets/ + examples/ + tests/ + benchmarks/.
- ASL spec version 1.0, format_version trên skill.yaml.
- Không registry: local-first. Không MCP.
