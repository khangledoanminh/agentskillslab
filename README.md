<div align="center">

# AgentSkillsLab

### Production-grade skills for coding agents

**Not just a `SKILL.md`. A self-contained developer tool: scripts, tests, benchmarks, security rules, examples — all verified before an agent ever runs it.**

[![MIT License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Python](https://img.shields.io/badge/python-%E2%89%A53.11-blue)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-35%20passing-brightgreen)](docs/AUDIT_SUMMARY.md)
[![Skills](https://img.shields.io/badge/skills-10%20flagship-purple)](skills)
[![Agent compat](https://img.shields.io/badge/agents-Claude%20Code%20%7C%20Codex%20%7C%20Cursor%20%7C%20Copilot%20%7C%20OpenCode%20%7C%20Kilo-orange)](docs/ADAPTER_NOTES.md)

</div>

---

## The problem

Coding agents today consume "skills" as glorified prompt fragments: a `SKILL.md` full of *"you are an expert programmer..."* with zero verification, zero tooling, zero safety. Nobody knows whether the skill works, whether it hallucinates its outputs, or whether it is teaching your agent to do something dangerous.

## The answer

Every skill in AgentSkillsLab is a **mini developer tool**:

```
skill/
├── SKILL.md              ← standardized frontmatter + agent workflow
├── skill.yaml            ← manifest: version, license, permissions, compatibility
├── SECURITY-ALLOW.md     ← explicit justification for every shell command
├── scripts/              ← deterministic tools that REALLY run
├── tests/                ← tests on real fixtures, asserting real results
├── benchmarks/           ← real timing (median / min / max)
├── examples/             ← end-to-end runnable demos
├── references/           ← rule references, CVE database
└── assets/
```

> **Design principle:** 10–20 deep skills, not 500 shallow ones. Whatever can be measured should be scripted; the AI does only analysis, judgment and explanation.

## The 10 flagship skills

| Skill | What it does | Proof it works |
|---|---|---|
| 🔐 **security-auditor** | Finds secrets, dangerous APIs, unsafe shell commands with evidence + severity | 26 scan rules → 5 real findings on a vulnerable fixture repo |
| 🕵️ **deep-debugger** | Error + stack trace + logs + git history → hypothesis → test each → root cause | Context collection from real repos with git log, env, diff |
| 💊 **dependency-doctor** | Outdated / vulnerable / unused / license conflicts for npm, pip, cargo, go | Embedded CVE database → 5 HIGH CVEs found (requests, pyyaml, flask, lodash, axios) |
| ⚡ **performance-engineer** | Benchmark → profile → bottleneck → patch → benchmark again | Real `perf_counter` + cProfile; naive_fib correctly identified as hotspot |
| 🧪 **test-engineer** | Uncovered paths → generate tests → run → **mutate** → coverage | Real line coverage 66.3% + real mutation score |
| 🧹 **refactor-engineer** | God class, long function, duplication, circular deps, bad abstractions | Correctly detects all 3 smells + dependency cycles |
| 🏗️ **codebase-architect** | Module map, coupling, hotspots + **auto-generated Mermaid diagram** | Dependency graph + cycle detection on multi-module fixture |
| 🧟 **repo-resurrection** | Dead repo → audit → restore env → fix deps → repair tests → modernize | State audit of a 4-years-stale repo |
| 🚀 **release-engineer** | Version bump, changelog, tests, security, license → release-ready? | Bool verdict + per-check report |
| 📚 **documentation-engineer** | Public-API doc coverage + verifies examples **actually run** | Real coverage % against live API count |

## Verified, not claimed

Before release, the whole project passed an independent audit ([docs/AUDIT_SUMMARY.md](docs/AUDIT_SUMMARY.md)):

| Check | Result |
|---|---|
| Platform tests | **25/25 PASS** (manifest, validator, scanner, runner, CLI) |
| Skill core tests | **10/10 PASS** (every script run on a real fixture) |
| Malformed fixtures | **17/17 rejected** by the validator |
| Malicious fixtures | **8/8 rejected** (prompt injection, path traversal, secret embedding, dependency confusion, exec injection) |
| Static analysis (ruff E/F/W) | **0 errors** |
| Benchmarks | Audit ~100 ms · security scan ~10 ms · validate 10 skills ~2 s |

## Security model — two-way

**Scanning skills** so your agent never learns something dangerous (SEC-001..006: secrets, shell exec, eval/exec, destructive commands, unsafe pickle/tempfile, prompt injection in docs). Any HIGH finding fails validation unless explicitly justified in `SECURITY-ALLOW.md` with file:line + reason.

**Running skills safely** via `lib/runner.py`: command denylist, hard timeout, environment isolation, and arguments always passed as a list — never `shell=True`.

## Quick start

```bash
git clone https://github.com/YOUR_USERNAME/agentskillslab.git
cd agentskillslab

# validate any skill (including ones you download from the wild)
python3 cli/agent_skills.py validate ./skills/security-auditor

# run its tests on real fixtures
python3 skills/security-auditor/tests/test_audit.py

# audit a repo — see 5 real findings
python3 skills/security-auditor/scripts/audit.py fixtures/repos/vulnerable-sample

# check dependency health — see 5 known CVEs
python3 skills/dependency-doctor/scripts/doctor.py fixtures/repos/vulnerable-sample
```

Copy any skill folder into your agent's skill directory and it just works — no MCP, no vendor lock-in. See [docs/ADAPTER_NOTES.md](docs/ADAPTER_NOTES.md) for Claude Code, Codex, Cursor, GitHub Copilot, OpenCode and Kilo.

## Roadmap

1.1: skill generator CLI, skill registry index, skill chaining, Rust port of the runtime. See [docs/ROADMAP.md](docs/ROADMAP.md).

## Docs

| File | Content |
|---|---|
| [spec/SKILL_SPEC.md](spec/SKILL_SPEC.md) | Skill Specification 1.0 + JSON schema |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Architecture |
| [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md) | STRIDE threat model |
| [docs/AUDIT_SUMMARY.md](docs/AUDIT_SUMMARY.md) | Full audit evidence |
| [docs/ADAPTER_NOTES.md](docs/ADAPTER_NOTES.md) | Per-agent install paths |
| [SECURITY.md](SECURITY.md) | Security policy & reporting |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute a skill |

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md). One deep skill beats ten shallow ones. PRs without tests are not merged

---

Built with ❤ by [khangledoanminh](https://github.com/khangledoanminh) — MIT License
