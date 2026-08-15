# AgentSkillsLab Skill Specification

**Version:** 1.0 · **Date:** August 15, 2026 · **Format version:** 1.0

---

## 1. Purpose

Spec này định nghĩa định dạng **Skill** của AgentSkillsLab (ASL). Mục tiêu kép: (a) tương thích ngược với định dạng Agent Skills mở của Anthropic (frontmatter `name` + `description` trong SKILL.md), để mọi skill ASL dùng được trực tiếp trong Claude Code, Codex, Cursor, GitHub Copilot, OpenCode, Kilo, VS Code; (b) bổ sung metadata, kiểm soát chất lượng và bảo mật mà định dạng gốc chưa có.

## 2. Conformance

Skill ASL 1.0 **BẮT BUỘC** tuân thủ tất cả yêu cầu §4. Skill chỉ-tương-thích-Anthropic (chỉ có SKILL.md hợp lệ) được coi là conformance cấp "basic" — validate qua được nhưng không có metadata mở rộng và sẽ nhận warning.

## 3. Directory Structure

```
my-skill/                       # tên thư mục = skill name
├── SKILL.md                    # BẮT BUỘC — frontmatter YAML + instructions
├── skill.yaml                  # BẮT BUỘC (ASL full) — metadata mở rộng
├── scripts/                    # OPTIONAL — scripts thực thi được
├── references/                 # OPTIONAL — reference docs (.md, .txt, .json)
├── assets/                     # OPTIONAL — templates, diagrams, data files
├── examples/                   # OPTIONAL — ví dụ chạy được
├── tests/                      # BẮT BUỘC nếu skill có scripts/
├── benchmarks/                 # OPTIONAL
└── requirements.txt            # OPTIONAL — Python dependencies của scripts
```

Quy tắc cấu trúc:

1. Tên thư mục, tên skill (frontmatter) và `name` trong skill.yaml phải **trùng nhau**.
2. Mọi tham chiếu file trong SKILL.md phải tồn tại thực tế trong skill dir (validator kiểm tra — mã lỗi V-014).
3. Scripts chỉ nằm trong `scripts/`; không cho phép file thực thi ở root skill dir (mã lỗi V-011).
4. `tests/` BẮT BUỘC nếu `scripts/` tồn tại và không rỗng (mã lỗi V-020).

## 4. Required Fields

### 4.1 SKILL.md frontmatter (Anthropic-compatible)

```yaml
---
name: my-skill                    # ≤64 chars, [a-z0-9-], không reserved words
description: >-                   # ≥30 chars, mô tả việc gì + KHI NÀO dùng
  Analyze X and do Y. Use when the user asks about X.
---
```

Ràng buộc: `name` không chứa "anthropic", "claude", "manus"; không trùng với skill khác trong cùng tập cài đặt (validator cảnh báo trùng tên, mã V-018).

### 4.2 skill.yaml (ASL metadata)

```yaml
format_version: "1.0"
version: "1.0.0"                  # semver
title: My Skill                   # human-readable
license: "MIT"                    # SPDX identifier
maintainer: "Name <email>"
compatibility:
  agents:                         # danh sách agent được verify
    - claude-code
    - codex
    - cursor
    - github-copilot
    - opencode
    - kilo
  requires:                       # external requirements
    - python: ">=3.10"
    - command: git
    - command: node
permissions:
  filesystem: local               # local | read-only | none
  network: none                   # none | outbound-only
  downloads: false
  install_packages: false
  subprocess: safe                # safe | none
  max_runtime_seconds: 300
dependencies:
  python: [pyyaml>=6.0]
  system: [git]
determinism: full                 # full | partial | ai-guided
tags: [security, audit]
```

Trường bắt buộc: `format_version`, `version`, `title`, `license`, `permissions`. `compatibility`, `dependencies`, `tags` optional nhưng `compatibility.agents` BẮT BUỘC nếu claim hỗ trợ agent (không được liệt kê agent chưa kiểm chứng — mã lỗi V-016).

## 5. Validation Rules (mã lỗi V-xxx)

| Mã | Rule | Severity |
|----|------|----------|
| V-001 | SKILL.md tồn tại, UTF-8, ≤500KB | error |
| V-002 | Frontmatter hợp lệ, có name + description | error |
| V-003 | name đúng pattern, không reserved | error |
| V-004 | description ≥30 chars, không rỗng | error |
| V-005 | skill.yaml tồn tại + parse được | error |
| V-006 | format_version = 1.0 | error |
| V-007 | version semver hợp lệ | error |
| V-008 | license SPDX hợp lệ | error |
| V-009 | permissions hợp lệ, đầy đủ | error |
| V-010 | name thư mục = name frontmatter = skill.yaml | error |
| V-011 | Không file thực thi ở root skill dir | error |
| V-012 | scripts chỉ chứa file biết trước (không binary không rõ nguồn gốc) | warning |
| V-013 | scripts syntax-check được (py_compile / bash -n) | error |
| V-014 | Mọi tham chiếu file trong SKILL.md tồn tại | error |
| V-015 | Phát hiện pattern độc hại (obfuscation, dangerous calls) | error |
| V-016 | compatibility.agents không claim quá phạm vi | warning |
| V-017 | dependencies cài được / tồn tại | warning |
| V-018 | Trùng tên với skill khác trong index | warning |
| V-019 | SKILL.md body >5000 tokens (khuyến nghị) | info |
| V-020 | tests/ tồn tại nếu scripts/ không rỗng | error |
| V-021 | tests chạy qua (khi `agent-skills test`) | error |
| V-022 | references/assets không chứa file nguy hiểm (.exe, .dll, .so) | error |
| V-023 | Symlinks trỏ ra ngoài skill dir | error |

## 6. Execution Safety Contract

Khi một agent (hoặc CLI) thực thi skill:

1. **Trước khi chạy bất kỳ script nào:** đọc `skill.yaml` permissions; hiển thị bản tóm tắt permissions cho user (CLI tự động, agent nên làm tương tự).
2. **Chạy trong envelope:** workdir = thư mục được chỉ định (không phải skill dir trừ khi user yêu cầu), timeout theo `max_runtime_seconds`, không shell injection (subprocess list args, không `shell=True`).
3. **Không auto-execution:** skill không được yêu cầu agent chạy script ngay khi load; chỉ chạy khi user đồng ý task đó.
4. **Findings phải có evidence:** script output JSON với `file`, `line`, `evidence`, `rule_id`; tuyệt đối không invent findings (nếu không quét được → trả về status "not_scanned", không phải danh sách rỗng).

## 7. Determinism Levels

| Level | Nghĩa | Yêu cầu |
|-------|-------|---------|
| `full` | Toàn bộ workflow chạy không cần LLM | scripts đủ cho mọi bước |
| `partial` | Một số bước cần LLM analysis | SKILL.md ghi rõ bước nào |
| `ai-guided` | Chủ yếu hướng dẫn LLM | scripts chỉ hỗ trợ |

Flagship skills của ASL hướng tới `full`/`partial` — AI enhances chứ không required.

## 8. Versioning & Evolution

Spec dùng semantic versioning. Thay đổi backward-compatible (thêm optional field) → format_version giữ 1.0, version minor bump. Breaking change → format_version 2.0. Validator luôn từ chối format_version không nhận dạng được (fail-safe).

## 9. Compatibility Matrix

| Agent | Cơ chế consume | ASL compatible? |
|-------|----------------|-----------------|
| Claude Code | `.claude/skills/`, frontmatter discovery | Có (frontmatter chuẩn) |
| Codex | skills directory + SKILL.md | Có |
| Cursor | agent rules/skills | Có |
| GitHub Copilot | custom instructions/skills | Có (read SKILL.md) |
| OpenCode | skills directory | Có |
| Kilo | SKILL.md folders | Có |
| VS Code agent | agent-customization skills | Có |

## 10. References

1. [Agent Skills open standard](https://agentskills.io/)
2. [Anthropic — Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
