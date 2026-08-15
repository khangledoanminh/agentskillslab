# Adapter Notes — Đưa skill vào từng coding agent

Skill trong AgentSkillsLab là artifact độc lập: không cần MCP server, không cần cài đặt đặc biệt của vendor. Việc "install" chỉ là copy thư mục skill vào skill path của agent. Tài liệu này chỉ rõ path và cách kích hoạt cho từng agent phổ biến.

## Tổng quan

Mọi agent hỗ trợ skills theo cơ chế giống nhau: một thư mục chứa các skill, mỗi skill là một thư mục con có `SKILL.md` ở gốc. Khi người dùng gọi tác vụ liên quan, agent đọc `SKILL.md` (frontmatter để match nhu cầu, body để biết quy trình), đọc các script và chạy chúng. AgentSkillsLab tuân thủ đúng cơ chế này nên **zero adaptation** cho phần consumption; khác biệt duy nhất là đường dẫn cài đặt.

## Từng agent

| Agent | Skill path | Cách cài | Ghi chú |
|---|---|---|---|
| **Claude Code** | `~/.claude/skills/<skill>/` | `cp -r skills/security-auditor ~/.claude/skills/` | Support skills từ SDK 2025-05-21. Agent tự đọc SKILL.md khi nhu cầu match description. Không cần đăng ký thêm. |
| **Codex (OpenAI)** | Theo `OPENAI_SKILLS_DIR` env var hoặc `<project>/.codex/skills/` | `export OPENAI_SKILLS_DIR=/path/to/agentskillslab/skills` | Mỗi skill cần thư mục riêng; SKILL.md phải có frontmatter hợp lệ (yêu cầu sẵn có trong spec 1.0). |
| **Cursor** | `.cursor/skills/<skill>/SKILL.md` trong repo | Copy vào repo, commit | Cursor đọc SKILL.md trong workspace; phù hợp chia sẻ skill cùng team qua repo. |
| **GitHub Copilot** | `.github/copilot-instructions.md` + skill system (mới) | Đưa nội dung workflow vào instructions hoặc skill dir theo docs GitHub | Skill system Copilot đang tiến hóa; nội dung workflow của SKILL.md body có thể port trực tiếp. |
| **OpenCode** | `~/.config/opencode/skills/<skill>/` (mặc định) | `cp -r skills/* ~/.config/opencode/skills/` | Tương thích gần như 1:1 với format Anthropic. |
| **Kilo Code** | `~/.kilo/skills/<skill>/` | Copy tương tự Claude Code | Fork VS Code, dùng chung cơ chế. |

## Nguyên tắc porting nội dung (nếu agent không đọc YAML)

Một số agent chỉ đọc `SKILL.md` markdown thuần, bỏ qua `skill.yaml`. Khi đó mọi thông tin quan trọng vẫn phải xuất hiện trong frontmatter của `SKILL.md` (đã làm sẵn): tên, description, version, compatibility, permissions. `skill.yaml` chỉ là manifest bổ sung cho tooling (CLI validate/inspect của chính AgentSkillsLab).

## Điều agent cần tuân thủ khi chạy skill

Khuyến nghị đưa đoạn sau vào system prompt / instructions khi dùng skills của thư viện này:

1. **Luôn chạy script qua CLI runner an toàn** nếu có thể: `agent-skills test <skill>` trước khi dùng trong repo thật.
2. **Không bỏ qua SECURITY-ALLOW.md**: chỉ các shell command đã được justify mới hợp pháp; nếu thấy pattern mới, yêu cầu agent giải thích trước khi chạy.
3. **Đọc cả references/ và examples/**: workflow trong SKILL.md body chỉ là khung; chi tiết rule/reference nằm trong references.
4. **Tôn trọng permissions** trong skill.yaml: skill khai báo `network: none` thì không được phép gọi network.

## Kiểm tra sau khi cài

```bash
# Validate skill vừa copy
agent-skills validate ~/.claude/skills/security-auditor

# Chạy test của skill trên máy đích
agent-skills test ~/.claude/skills/security-auditor
```
