# Changelog

Tất cả thay đổi đáng chú ý của AgentSkillsLab được ghi nhận trong tài liệu này theo định dạng [Keep a Changelog](https://keepachangelog.com/), phiên bản theo [Semantic Versioning](https://semver.org/).

## [1.0.0] — 2026-08-15

Phiên bản phát hành đầu tiên — hoàn chỉnh spec, platform, 10 flagship skills và bộ audit.

### Added — Spec & Platform

- **Skill Specification 1.0** (`spec/SKILL_SPEC.md`, `spec/schema.json`): frontmatter chuẩn, manifest YAML, permission declaration, determinism level, compatibility, versioning semver.
- **CLI `agent-skills`**: `validate`, `test`, `benchmark`, `inspect`, `search`, `doctor`, `version`.
- **lib/manifest.py**: parse frontmatter + skill.yaml, kiểm reserved words, validate version.
- **lib/validator.py**: 22 rules (V-001..V-022) — cấu trúc, syntax scripts, references an toàn, tests bắt buộc, permission consistency, resource limits.
- **lib/security.py**: engine quét 6 nhóm rule SEC-001..006 (secrets, shell exec, eval/exec, sudo/rm-rf, pickle/tempfile, prompt injection), severity gate HIGH/CRITICAL → FAIL trừ khi justify trong SECURITY-ALLOW.md.
- **lib/runner.py**: safe script execution — denylist command, timeout, env isolation, command injection prevention (args dạng list, không shell=True).
- **lib/index.py**: search index (inverted index, fuzzy matching, relevance ranking).
- **lib/benchmarks.py**: timing framework (median/min/max/p95, CPU time, memory RSS).
- **Bộ fixture fuzzing**: 3 valid + 17 malformed + 8 malicious.

### Added — 10 flagship skills

- **security-auditor**: 26 scan rules, audit fixture vulnerable-sample → 5 findings.
- **deep-debugger**: collect_context gom git log + environment + diff; workflow hypothesis-driven.
- **dependency-doctor**: CVE database embedded (nguồn + ngày), phát hiện 5 CVE HIGH trên fixture; outdated/unused/conflict/license checks.
- **performance-engineer**: profile_code (perf_counter + cProfile top-10) + compare before/after.
- **test-engineer**: coverage_report (coverage thật 66.3% trên fixture) + mutate (mutation score thật).
- **refactor-engineer**: detect_smells (god class, long function, duplication) + import_graph (cycle detection, grouped packages).
- **codebase-architect**: graph_deps (adjacency, cycles, hotspots, metrics) + Mermaid diagram auto-gen + verify roundtrip.
- **repo-resurrection**: audit_state (missing CI/docs/tests/CHANGELOG, secret scan, dependency health).
- **release-engineer**: release_check (version bump, changelog, tests, security, licenses) → release_ready bool.
- **documentation-engineer**: doc_coverage (public API coverage) + check_examples (chạy ví dụ thật).

### Added — Quality & docs

- 25/25 platform tests PASS; 10 test_core PASS; ruff 0 error.
- Benchmarks: audit ~100ms, validate 10 skills ~2s/loop.
- SECURITY-ALLOW.md mechanism cho shell commands hợp pháp.
- Tài liệu: RFC, ARCHITECTURE, THREAT_MODEL, TESTING_STRATEGY, ROADMAP, ADAPTER_NOTES, AUDIT_SUMMARY, CHANGELOG, SECURITY, CONTRIBUTING.

## [1.1.0 planned] — xem ROADMAP.md

Dự kiến: skill generator CLI, skill marketplace index, skill chaining, Windows testing, Rust port của runner.
