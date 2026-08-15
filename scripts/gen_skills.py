#!/usr/bin/env python3
"""Sinh cấu trúc thư mục + SKILL.md + skill.yaml cho các flagship skill.

Chạy 1 lần để tạo khung; nội dung chi tiết (scripts/tests/benchmarks) viết riêng.
Không đè file đã tồn tại.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "skills"

SKILLS: list[dict] = [
    {
        "name": "deep-debugger",
        "title": "Deep Debugger",
        "license": "MIT",
        "tags": ["debugging", "root-cause", "troubleshooting"],
        "determinism": "partial",
        "desc": "Root-cause debugging workflow: reconstruct error context, build hypotheses, test each hypothesis against evidence, and prove the root cause with a reproducer. Use when debugging a failing test, crash, or confusing error message and you need to find the actual root cause rather than guess fixes.",
        "body": """# Deep Debugger

Tìm root cause thật, không đoán mò. Quy trình: **Tái hiện → Thu thập → Giả thuyết → Kiểm chứng → Chứng minh → Fix có test**.

## Quy trình (6 bước)

1. **Tái hiện lỗi**: chạy lại đúng lệnh/context lỗi được báo cáo. Nếu không tái hiện được, dừng và hỏi thêm thông tin. Không fix khi chưa tái hiện.
2. **Thu thập context**: stack trace đầy đủ, logs, environment (OS, phiên bản, config), git history gần đây (`git log -p -5`), source file liên quan.
3. **Dựng giả thuyết (≥2)**: từ evidence, liệt kê các root cause có thể, xếp theo xác suất. Ghi rõ evidence ủng hộ/phản bác từng giả thuyết.
4. **Kiểm chứng từng giả thuyết**: dùng debugger/bisect/logs để loại trừ. Mỗi lần loại trừ ghi lại lý do.
5. **Chứng minh root cause**: viết minimal reproducer — đoạn code nhỏ nhất tái hiện lỗi. Nếu reproducer fail → root cause xác nhận.
6. **Fix + regression test**: sửa tại root cause (không workaround symptom), thêm test tái hiện lỗi để đảm bảo không tái diễn.

## Nguyên tắc

- Evidence trước, kết luận sau. Không bỏ qua dòng log nào trong stack trace.
- Nếu evidence mâu thuẫn, quay lại bước 2 thay vì ép giả thuyết.
- Repro case là bằng chứng: phải kèm theo báo cáo final.
- Không bao giờ sửa nhiều chỗ cùng lúc khi chưa biết root cause.

## Scripts

- `scripts/collect_context.py <repo> [--log FILE]` — trích stack trace, git history 5 commit gần, file list có sửa gần đây.
- `scripts/hypothesis.md` — template bảng giả thuyết (AI điền).

## References

- [WORKFLOW.md](references/WORKFLOW.md) — chi tiết từng bước với ví dụ thật
- [HYPOTHESIS-TEMPLATE.md](references/HYPOTHESIS-TEMPLATE.md) — template bảng giả thuyết
""",
    },
    {
        "name": "test-engineer",
        "title": "Test Engineer",
        "license": "MIT",
        "tags": ["testing", "coverage", "mutation", "quality"],
        "determinism": "partial",
        "desc": "Coverage-driven test engineering: analyze code, find uncovered paths, generate tests targeting them, run, measure coverage, mutate to verify test strength, and iterate until quality targets are met. Use when asked to write tests, improve test coverage, or verify that existing tests actually catch bugs.",
        "body": """# Test Engineer

Viết test có mục tiêu, không viết test cho đủ số. Vòng lặp: **inspect → uncovered paths → generate → run → coverage → mutate → improve → dừng khi đạt target**.

## Quy trình (7 bước)

1. **Inspect code**: đọc module, xác định hàm public, branches, edge cases, error paths.
2. **Tìm uncovered paths**: chạy coverage tool (`python3 -m pytest --cov`) để lấy coverage report thật. KHÔNG đoán coverage bằng mắt.
3. **Generate tests**: ưu tiên branch chưa cover, edge cases (empty, None, boundary, error paths). Mỗi test có tên mô tả hành vi + assert cụ thể.
4. **Run**: chạy toàn bộ suite, mọi test phải pass.
5. **Measure coverage**: lấy line + branch coverage thật từ tool. Ghi số trước/sau.
6. **Mutate** (nếu mutation tool có): chạy mutant (VD thay `+` thành `-`, đổi điều kiện). Test mạnh phải kill mutant. Tỉ lệ survive cao = test yếu dù coverage cao.
7. **Improve**: dựa vào mutant survive + branch miss, viết thêm test. Lặp 3–7 cho tới: coverage mục tiêu (VD ≥80%) VÀ mutant kill rate ≥70%.

## Quality targets mặc định

| Metric | Target |
|--------|--------|
| Line coverage | ≥ 80% |
| Branch coverage | ≥ 70% |
| Mutation kill rate | ≥ 70% |
| Flaky tests | 0 (chạy 3 lần phải nhất quán) |

## Nguyên tắc

- Test hành vi, không test implementation detail (trừ khi cố ý contract test).
- Test phải deterministic; không dùng sleep/rand mà không seed.
- Coverage 100% không phải mục tiêu — diminishing returns; dừng khi đạt target + chi phí hợp lý.
- Test file đặt cạnh code hoặc trong tests/, tên rõ ràng.

## Scripts

- `scripts/coverage_report.py <module-dir> [--target N]` — chạy pytest --cov, xuất JSON coverage thật.
- `scripts/mutate.py <module> [--operator list]` — simple mutator: thay arithmetic/condition operators, chạy test, báo mutant survive/kill.

## References

- [COVERAGE-GUIDE.md](references/COVERAGE-GUIDE.md)
- [MUTATION-REFERENCE.md](references/MUTATION-REFERENCE.md)
""",
    },
    {
        "name": "dependency-doctor",
        "title": "Dependency Doctor",
        "license": "MIT",
        "tags": ["dependencies", "supply-chain", "security", "maintenance"],
        "determinism": "full",
        "desc": "Diagnose dependency health across package managers (npm/pip/cargo/go): outdated packages, known vulnerabilities, unused dependencies, version conflicts, and license compliance issues, then produce a prioritized remediation plan. Use when managing, upgrading, or auditing project dependencies.",
        "body": """# Dependency Doctor

Chẩn đoán sức khỏe dependencies bằng dữ liệu THẬT từ package manager, không đoán. Đầu ra: bảng vấn đề + plan fix ưu tiên + lệnh chạy được.

## Quy trình (5 bước)

1. **Detect ecosystem**: tìm lockfile/manifest (package-lock.json, requirements.txt, Cargo.toml, go.sum, pyproject.toml). Báo ecosystem phát hiện.
2. **Quét vấn đề** (chạy script thật):
   - `scripts/doctor.py <repo>` chạy các check: outdated (so lockfile vs registry khi có network, hoặc heuristic version pattern khi không), vulnerable (so version với CVE database embedded `references/cves.json`), unused (import analysis), conflicts, license.
3. **Phân loại severity**: CRITICAL (CVE exploited), HIGH (CVE có fix), MEDIUM (outdated major), LOW (license info/unused).
4. **Remediation plan**: thứ tự fix, lệnh upgrade cụ thể, cảnh báo breaking change, backup trước khi upgrade.
5. **Verify sau fix**: chạy lại doctor, xác nhận vấn đề giảm; chạy test suite repo nếu có.

## Nguyên tắc

- Mọi con số (số package, version, CVE) phải từ output của script thật, không ước lượng.
- Không tự động chạy `upgrade` không hỏi — luôn đưa plan trước, đợi xác nhận.
- Lockfile là source of truth; không sửa file thủ công.
- Nếu không có network: chạy chế độ offline (check syntax, lockfile consistency, embedded CVE list), ghi rõ giới hạn.

## Scripts

- `scripts/doctor.py <repo> [--ecosystem pip|npm|cargo|go] [--offline] [--output report.json]`

## References

- [ECOSYSTEMS.md](references/ECOSYSTEMS.md) — đặc thù từng package manager
- [CVE-LIMITATIONS.md](references/CVE-LIMITATIONS.md) — giới hạn database embedded
""",
    },
    {
        "name": "performance-engineer",
        "title": "Performance Engineer",
        "license": "MIT",
        "tags": ["performance", "profiling", "optimization", "benchmarking"],
        "determinism": "partial",
        "desc": "Evidence-based performance optimization: benchmark the real code before and after changes, profile to find the true bottleneck, patch, and verify improvement with statistical rigor. Use when code is slow, latency needs reducing, or optimization claims must be proven.",
        "body": """# Performance Engineer

Tối ưu dựa trên số liệu THẬT, không dựa trên cảm giác. Pipeline: **benchmark trước → profile → xác định bottleneck → patch → benchmark lại → so sánh thống kê**.

## Quy trình (6 bước)

1. **Benchmark baseline**: chạy code thật nhiều lần (≥5 iterations), lấy median + p95. Ghi environment (OS, Python, CPU). Không dùng 1 lần đo.
2. **Profile**: dùng cProfile/timeit/line_profiler trên workload thật. Xác định top-3 hàm tốn thời gian nhất.
3. **Identify bottleneck**: chọn 1 bottleneck lớn nhất có evidence rõ (phần trăm thời gian). KHÔNG tối ưu nhiều chỗ cùng lúc.
4. **Patch**: sửa tối thiểu tại bottleneck. Ghi rõ giả thuyết cải thiện.
5. **Benchmark again**: cùng workload, cùng environment, ≥5 iterations. Tính speedup = median_before / median_after.
6. **Verify**: speedup ≥20% mới coi là significant; kiểm tra correctness (output không đổi); kiểm tra không phá trade-off (memory, readability).

## Nguyên tắc

- Median, không mean (chống outlier).
- Warmup trước khi đo.
- Một thay đổi một lần — isolate variable.
- Không optimze premature: chỉ tối ưu khi có số liệu chậm thật.
- Nếu patch làm chậm: revert, ghi lại learning.

## Scripts

- `scripts/profile_code.py <target> [--iterations N]` — wrapper cProfile + timing median.
- `scripts/compare.py before.json after.json` — so 2 kết quả benchmark, tính speedup + verdict.

## References

- [PROFILING-TOOLS.md](references/PROFILING-TOOLS.md)
- [STATS-NOTES.md](references/STATS-NOTES.md) — tại sao median, outlier handling
""",
    },
    {
        "name": "refactor-engineer",
        "title": "Refactor Engineer",
        "license": "MIT",
        "tags": ["refactoring", "code-quality", "technical-debt", "design"],
        "determinism": "partial",
        "desc": "Detect code smells (God class, long functions, duplication, circular dependencies, bad abstractions) with real static analysis, refactor safely with regression tests as guardrails, and verify no behavior change. Use when improving code structure, reducing technical debt, or preparing legacy code for extension.",
        "body": """# Refactor Engineer

Refactor an toàn = **phát hiện thật + regression guard + verify behavior không đổi**. Không refactor vì thích — refactor vì có smell cụ thể và risk được kiểm soát.

## Quy trình (6 bước)

1. **Phát hiện smells** (script thật): chạy `scripts/detect_smells.py <repo>` — tìm God class (>500 dòng, >15 method), long function (>50 dòng, >4 nested), duplication (clone detection qua normalized hashing), circular dependency (import graph), bad abstraction (deep inheritance, shotgun surgery indicators).
2. **Chọn mục tiêu**: 1 smell, ưu tiên theo: frequency × sửa dễ × impact. Không refactor toàn repo cùng lúc.
3. **Establish guardrails**: chạy regression test suite hiện có (hoặc viết characterization test nếu chưa có) — green trước khi chạm code.
4. **Refactor từng bước nhỏ**: mỗi bước giữ behavior, chạy regression sau mỗi bước. Commit riêng từng bước.
5. **Verify**: regression suite green + diff behavior kiểm tra (output các entry point không đổi) + re-run smell detector xác nhận smell giảm.
6. **Report**: bảng smell trước/sau, danh sách commits, risk còn lại.

## Nguyên tắc

- Behavior preservation là bất biến — test fail = revert.
- Một smell một lần refactor.
- Không đổi API public nếu không cần; nếu đổi, cập nhật callers cùng lúc + doc.
- Refactor nhỏ > refactor lớn.

## Scripts

- `scripts/detect_smells.py <repo> [--thresholds FILE]` — output JSON smells với severity.
- `scripts/import_graph.py <repo>` — vẽ dependency graph, phát hiện cycle.

## References

- [SMELL-CATALOG.md](references/SMELL-CATALOG.md) — định nghĩa + ngưỡng từng smell
- [SAFETY-CHECKLIST.md](references/SAFETY-CHECKLIST.md)
""",
    },
    {
        "name": "codebase-architect",
        "title": "Codebase Architect",
        "license": "MIT",
        "tags": ["architecture", "analysis", "visualization", "documentation"],
        "determinism": "full",
        "desc": "Analyze a repository's architecture and produce an evidence-based architecture report: module map, dependency graph, coupling metrics, circular dependencies, and hotspot identification, with Mermaid diagrams generated from real import relationships. Use when onboarding to a new codebase, planning major changes, or documenting system structure.",
        "body": """# Codebase Architect

Phân tích kiến trúc repo bằng dữ liệu THẬT từ import/dependency relationships, không bằng cảm nhận. Đầu ra: báo cáo kiến trúc + diagram Mermaid tự sinh.

## Quy trình (5 bước)

1. **Map modules**: liệt kê packages/modules, kích thước (dòng code), trách nhiệm suy ra từ tên + docstring.
2. **Build dependency graph**: chạy `scripts/graph_deps.py <repo>` phân tích import statements → adjacency list thật.
3. **Tính metrics**:
   - Coupling: số dependency in/out mỗi module (Ca/Ce).
   - Circular dependencies: DFS tìm cycle trong import graph.
   - Hotspots: module có fan-in cao (nhiều nơi phụ thuộc) + thay đổi gần đây (git log).
4. **Vẽ diagram**: sinh Mermaid flowchart từ graph thật; KHÔNG vẽ tay diagram không khớp code.
5. **Báo cáo**: module map + metrics table + cycle list + hotspot ranking + khuyến nghị tách module nếu coupling quá cao.

## Nguyên tắc

- Mọi con số từ script; diagram phải khớp graph thật (test: parse lại diagram phải bằng graph).
- Không phán kiến trúc "tốt/xấu" chung chung — chỉ ra metric cụ thể và ngưỡng.
- Report ngắn gọn: table + diagram + 5 khuyến nghị tối đa.

## Scripts

- `scripts/graph_deps.py <repo> [--language python|js|ts] [--output graph.json]`
- `scripts/metrics.py graph.json` — tính Ca/Ce, cycles, hotspots → JSON.

## References

- [METRICS-DEFINITIONS.md](references/METRICS-DEFINITIONS.md)
- [DIAGRAM-RULES.md](references/DIAGRAM-RULES.md)
""",
    },
    {
        "name": "repo-resurrection",
        "title": "Repo Resurrection",
        "license": "MIT",
        "tags": ["legacy", "maintenance", "modernization", "migration"],
        "determinism": "partial",
        "desc": "Revive an abandoned repository: audit its state, restore the build environment, fix broken dependencies and tests, modernize code and tooling, generate documentation, and produce a migration plan to bring the project back to life. Use when inheriting a dead or broken project that needs to become buildable, testable, and maintainable again.",
        "body": """# Repo Resurrection

Hồi sinh repo chết theo thứ tự: **audit → environment → dependencies → tests → code → docs → migration plan**. Mỗi bước có exit criterion rõ.

## Quy trình (7 bước)

1. **Audit**: đọc README/docs cũ, last commit, CI config, lockfile. Chạy `scripts/audit_state.py <repo>` → trạng thái: build broken? tests? dependency age? docs dead links?
2. **Restore environment**: dựng env chạy được (venv/container). Ghi lại chính xác steps + phiên bản tool — đây là deliverable quan trọng nhất.
3. **Fix dependencies**: cập nhật package tới version build được + không vulnerable. Giữ lockfile mới.
4. **Repair tests**: làm test suite chạy lại. Nếu test quá cũ không sửa được: viết characterization test mới covering core behavior.
5. **Modernize code**: chỉ các thay đổi cần để build/test pass + security fixes. KHÔNG rewrite theo ý thích — giữ behavior.
6. **Generate docs**: README mới (setup, run, test, architecture ngắn), docstring thiếu, changelog từ git history.
7. **Migration plan**: roadmap từng giai đoạn (1: build/test xanh; 2: dependency current; 3: feature parity; 4: CI tự động) + risk từng giai đoạn.

## Exit criteria

| Bước | Criterion |
|------|-----------|
| 2 | `make build`/equivalent pass trong env mới |
| 3 | Không dependency vulnerable đã biết (embedded CVE check) |
| 4 | ≥1 test suite chạy xanh |
| 5 | Behavior test không đổi |
| 6 | README mới tồn tại + setup chạy được từ README |
| 7 | Migration plan written + review-ready |

## Nguyên tắc

- Behavior preservation tuyệt đối — project sống lại, không biến thành project khác.
- Document mọi decision: vì sao upgrade version X mà không phải Y.
- Nếu repo quá lớn: resurrect core module trước, module còn lại trong migration plan.

## Scripts

- `scripts/audit_state.py <repo>` — báo cáo trạng thái repo cũ (last commit age, CI, deps, tests, docs).

## References

- [AUDIT-CHECKLIST.md](references/AUDIT-CHECKLIST.md)
- [MODERNIZATION-GUIDE.md](references/MODERNIZATION-GUIDE.md)
""",
    },
    {
        "name": "release-engineer",
        "title": "Release Engineer",
        "license": "MIT",
        "tags": ["release", "ci-cd", "packaging", "versioning"],
        "determinism": "full",
        "desc": "Prepare and validate a release: check changelog completeness, version bump consistency, build artifacts, license compliance, and release checklist items, producing a validated release manifest. Use when cutting a new version, preparing packages for distribution, or auditing release readiness.",
        "body": """# Release Engineer

Release readiness được CHỨNG MINH bằng checklist chạy thật, không khai báo. Pipeline: **read state → check items thật → build artifact → verify artifact → manifest**.

## Quy trình (5 bước)

1. **Đọc trạng thái**: current version (từ package metadata), git tag gần nhất, CHANGELOG entries chưa release.
2. **Check items thật** (script): CHANGELOG entry tồn tại cho version mới? version bump nhất quán (metadata == tag == changelog)? tests pass? build artifact tạo được? license file tồn tại? binary không lọt vào artifact source dist?
3. **Build artifact**: chạy build command thật của repo (python build, npm pack, cargo build).
4. **Verify artifact**: artifact tồn tại, size hợp lý, chứa đủ file cần (entry point, LICENSE), không chứa file nhạy cảm (secret scan nhanh).
5. **Manifest**: output JSON release manifest — mọi item pass/fail với evidence.

## Nguyên tắc

- Không tag/publish tự động — skill chỉ chuẩn bị + verify, publish là decision của người.
- Mọi check có evidence (file path, hash, command output).
- Version scheme tuân thủ semver; giải thích major/minor/patch choice.

## Scripts

- `scripts/release_check.py <repo> [--version NEXT]` — chạy mọi check, output manifest JSON.

## References

- [CHECKLIST-REFERENCE.md](references/CHECKLIST-REFERENCE.md)
- [SEMVER-GUIDE.md](references/SEMVER-GUIDE.md)
""",
    },
    {
        "name": "documentation-engineer",
        "title": "Documentation Engineer",
        "license": "MIT",
        "tags": ["documentation", "onboarding", "api-docs", "quality"],
        "determinism": "partial",
        "desc": "Assess and repair documentation quality with measurable checks: missing docstrings, undocumented public APIs, dead links, stale examples, and readability scoring, then generate documentation that matches the current code exactly. Use when docs are missing, outdated, or an onboarding guide is needed.",
        "body": """# Documentation Engineer

Docs phải khớp code THẬT tại thời điểm viết. Pipeline: **audit coverage thật → tìm lỗ hổng → viết từ source code hiện tại → verify links + examples chạy được**.

## Quy trình (5 bước)

1. **Audit coverage**: chạy `scripts/doc_coverage.py <repo>` — % public functions/classes có docstring, % modules có README, dead links trong markdown.
2. **Prioritize gaps**: public API không có doc > nội bộ > ví dụ cũ. Ưu tiên API public trước.
3. **Generate docs từ code thật**: parse signature + docstring hiện có + source body; viết docs mô tả đúng behavior hiện tại. KHÔNG extrapolate tính năng chưa có trong code.
4. **Verify examples**: mỗi code example trong docs phải chạy được (script chạy example, kiểm exit code).
5. **Verify links**: scan mọi link trong docs → target tồn tại (file local phải tồn tại; URL external đánh dấu cần manual verify).

## Metrics mặc định

| Metric | Target |
|--------|--------|
| Public API doc coverage | ≥ 90% |
| Dead internal links | 0 |
| Runnable examples | 100% ví dụ có code block |

## Nguyên tắc

- Docs mô tả behavior hiện tại; nếu code sai, báo bug riêng — không viết docs theo ý muốn.
- Ví dụ phải chạy; ví dụ không chạy worse hơn không có ví dụ.
- Markdown nhất quán: heading levels, code fence language.

## Scripts

- `scripts/doc_coverage.py <repo> [--output report.json]`
- `scripts/check_examples.py <docs-dir>` — chạy code blocks trong markdown

## References

- [STYLE-GUIDE.md](references/STYLE-GUIDE.md)
- [EXAMPLE-RULES.md](references/EXAMPLE-RULES.md)
""",
    },
]

DIRS = ["scripts", "references", "tests", "benchmarks", "examples"]


def gen(skill: dict) -> str:
    d = ROOT / skill["name"]
    if d.exists():
        return f"SKIP {skill['name']} (đã tồn tại)"

    d.mkdir(parents=True)
    for sub in DIRS:
        (d / sub).mkdir()

    # SKILL.md
    import re as _re

    def yaml_quote(text: str) -> str:
        """Quote description nếu chứa ký tự khiến YAML mapping value lỗi."""
        if _re.search(r": |#|\n|['\"]", text):
            safe = text.replace('"', '\\"').replace("\n", " ")
            return f'"{safe}"'
        return text

    (d / "SKILL.md").write_text(
        "---\n"
        f"name: {skill['name']}\n"
        f"description: {yaml_quote(skill['desc'])}\n"
        "---\n\n"
        + skill["body"],
        encoding="utf-8",
    )

    # skill.yaml
    (d / "skill.yaml").write_text(
        "format_version: \"1.0\"\n"
        f"version: \"1.0.0\"\n"
        f"title: {skill['title']}\n"
        f"description: {skill['desc']}\n"
        f"license: {skill['license']}\n"
        "maintainer: \"ASL Team <team@agentskillslab.dev>\"\n"
        "compatibility:\n"
        "  agents: [claude-code, codex, cursor, github-copilot, opencode, kilo]\n"
        "  requires:\n"
        "    - python: \">=3.10\"\n"
        "permissions:\n"
        "  filesystem: local\n"
        "  network: none\n"
        "  downloads: false\n"
        "  install_packages: false\n"
        "  subprocess: safe\n"
        "  max_runtime_seconds: 300\n"
        f"determinism: {skill['determinism']}\n"
        f"tags: {skill['tags']}\n",
        encoding="utf-8",
    )
    return f"OK   {skill['name']}"


def main() -> int:
    for skill in SKILLS:
        print(gen(skill))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
