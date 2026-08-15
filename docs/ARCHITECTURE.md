# AgentSkillsLab — Architecture

**Version:** 1.0 · **Date:** August 15, 2026 · **Authors:** AgentSkillsLab Maintainers

---

## 1. System Overview

AgentSkillsLab gồm ba lớp tách biệt:

| Lớp | Thành phần | Trách nhiệm |
|-----|-----------|-------------|
| **Spec** | `SKILL_SPEC.md`, JSON schema (`spec/schema.json`) | Định nghĩa format Skill v1.0 |
| **Library + CLI** | `lib/`, `cli/` | Validate, test, benchmark, inspect, search, doctor |
| **Skills** | `skills/` (10 flagship) | Các capability đóng gói hoàn chỉnh |

Ba lớp tách biệt để spec tồn tại độc lập với implementation: một agent bất kỳ có thể đọc `SKILL_SPEC.md` và tiêu thụ skill mà không cần cài `agent-skills`.

## 2. Repository Layout

```
agentskillslab/
├── SKILL_SPEC.md            # (tại spec/)
├── spec/
│   ├── SKILL_SPEC.md
│   ├── schema.json          # JSON Schema draft-07
│   └── schema-v1.yaml       # human-readable
├── cli/
│   ├── agent_skills.py      # entry point
│   └── commands/            # validate, test, benchmark, inspect,
│                            # search, install, update, remove, doctor
├── lib/
│   ├── validator.py         # skill validation engine
│   ├── runner.py            # safe script execution (permission sandbox)
│   ├── security.py          # dangerous-pattern detection dùng chung
│   ├── manifest.py          # parse skill.yaml + frontmatter
│   ├── index.py             # skill search index
│   ├── benchmarks.py        # timing framework (true metrics)
│   └── common.py            # paths, constants, error types
├── skills/
│   ├── security-auditor/
│   ├── deep-debugger/
│   ├── test-engineer/
│   ├── dependency-doctor/
│   ├── performance-engineer/
│   ├── refactor-engineer/
│   ├── codebase-architect/
│   ├── repo-resurrection/
│   ├── release-engineer/
│   └── documentation-engineer/
├── tests/                   # project tests (unit + integration + e2e)
├── fixtures/                # valid / malformed / malicious skills
├── benchmarks/              # project benchmarks (validator perf...)
└── docs/
```

Mỗi skill:

```
security-auditor/
├── SKILL.md              # Anthropic-compatible frontmatter + instructions
├── skill.yaml            # ASL metadata: version, license, deps,
│                         # compatibility, permissions, requirements
├── scripts/              # thực thi được (chmod +x không bắt buộc)
├── references/           # reference docs
├── assets/               # diagrams, templates
├── examples/             # ví dụ chạy được
├── tests/                # test riêng của skill
└── benchmarks/           # benchmark riêng
```

## 3. Key Design Decisions

### D1. Skill format: SKILL.md + skill.yaml (thay vì chỉ frontmatter)

**Chosen:** SKILL.md giữ frontmatter `name` + `description` chuẩn Anthropic (compatibility tối đa); metadata mở rộng (version, license, dependencies, compatibility, permissions, requirements) nằm trong `skill.yaml`.

**Alternatives:** (a) tất cả trong frontmatter → frontmatter phình to, khó evolve schema; (b) chỉ skill.yaml → mất khả năng Claude auto-discover khi đặt vào `.claude/skills/`.

**Trade-off:** hai nguồn metadata cần giữ đồng bộ → validator kiểm tra name/description khớp giữa SKILL.md và skill.yaml (kiểm chứng được).

### D2. Ngôn ngữ CLI/library: Python stdlib + pyyaml

**Chosen:** Python 3.10+, dependency duy nhất `pyyaml` (fallback parser nội bộ nếu không cài). CLI khởi động < 100ms cho `--help`.

**Alternatives:** Rust/Go binary → khởi động nhanh hơn nhưng barrier đóng góp cao; cài đặt phức tạp hơn cho người dùng. Node → xung đột ecosystem với skills JS.

**Reasoning:** Python là ngôn ngữ phổ biến nhất trong coding-agent scripts; contributor hiểu được code ngay; test nhanh với pytest.

### D3. Chạy scripts: sandbox permissions (không phải container)

**Chosen:** `runner.py` thực thi script trong một "permission envelope" kiểm soát: working-directory giới hạn, denylist shell-builtins nguy hiểm (`rm -rf /` patterns), timeout, không network nếu skill khai báo `permissions.network: none`. Lỗi permission → FAIL an toàn kèm diagnostic.

**Alternatives:** container (Docker) → isolation mạnh nhưng nặng, không portable trên Windows/Mac mặc định.

**Scalability:** container có thể thêm sau dưới dạng execution-backend; envelope đủ cho validate/test trên máy local.

### D4. Validator: fail-fast với danh sách lỗi, không exit ngay lỗi đầu

**Chosen:** validator thu thập TẤT CẢ lỗi/warning, trả về báo cáo có mã lỗi (V-xxx) và xếp hạng severity (error/warning/info). Exit code 1 nếu có bất kỳ error.

**Reasoning:** người dùng cần sửa hết lỗi trong một lần chạy, không chạy-đợi-sửa-lặp lại.

### D5. AI là optional layer

Validator, runner, index đều pure-deterministic. Các skill flagship ghi rõ bước nào chạy script (deterministic) và bước nào cần LLM (analysis), kèm "nếu không có LLM thì làm gì".

## 4. Data Flow

```
User request "audit repo X for security"
  → agent (Claude Code/Codex/...) discovers skill qua name+description (frontmatter)
  → agent reads SKILL.md instructions
  → instructions: step 1-5 chạy scripts/scan_secrets.py (deterministic, output JSON)
  → agent phân tích findings.json, quyết định severity, viết báo cáo
```

CLI `agent-skills test security-auditor` chạy tests/ của skill; `agent-skills benchmark ...` chạy benchmarks/.

## 5. Cross-Agent Compatibility Strategy

Mỗi skill khai báo trong `skill.yaml`:

```yaml
compatibility:
  agents: [claude-code, codex, cursor, github-copilot, opencode, kilo]
  requirements:
    - python >= 3.10
    - command: git
```

Điều kiện tương thích: (1) SKILL.md dùng frontmatter chuẩn; (2) scripts portable (POSIX sh hoặc Python); (3) không giả định thư mục cài đặt cụ thể; (4) chỉ tham chiếu file theo path tương đối.

## 6. Error Model

Tất cả lỗi CLI dùng một enum `ExitCode`: OK=0, VALIDATION_FAILED=2, RUNTIME_ERROR=3, SECURITY_VIOLATION=4, USAGE_ERROR=64. Message lỗi kèm mã lỗi để tra cứu trong docs.

## 7. Scalability Considerations

Index tìm kiếm dùng inverted index trong bộ nhớ, build từ filesystem — verified cho 1.000 skills trong < 5s (xem benchmark). Validator đọc skill tuần tự; có thể parallel hóa bằng `--parallel` khi cần. Không global state ẩn; mọi state nằm trong thư mục skill.

## 8. Technical Debt Register

| ID | Item | Severity | Kế hoạch |
|----|------|----------|----------|
| TD-1 | Fallback YAML parser nội bộ chỉ hỗ trợ subset | LOW | Document rõ; yêu cầu pyyaml cho production |
| TD-2 | Network-restriction là deny-based heuristic | MEDIUM | Audit định kỳ denylist |
| TD-3 | Chưa có execution-backend container | LOW | Roadmap v1.1 |
