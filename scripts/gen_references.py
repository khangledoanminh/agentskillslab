#!/usr/bin/env python3
"""Tạo reference files bắt buộc (được tham chiếu trong SKILL.md) cho 9 skill.

Mỗi file reference là tài liệu ngắn nhưng có nội dung thật, không placeholder rỗng.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "skills"


def w(skill: str, name: str, content: str) -> None:
    p = ROOT / skill / "references" / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content + "\n", encoding="utf-8")


# ---------------------------------------------------------------- deep-debugger
w("deep-debugger", "WORKFLOW.md", """# Deep Debugger Workflow — Chi tiết từng bước

## Bước 2: Thu thập context — checklist

| Item | Lệnh | Mục đích |
|------|------|----------|
| Stack trace đầy đủ | copy từ log, KHÔNG tóm tắt | Xác định call chain |
| Git history gần | `git log -p -5 -- <file>` | Tìm commit giới thiệu bug |
| Environment | `python --version`, `uname -a`, config | Loại trừ môi trường |
| Log quanh lỗi | `grep -B20 -A20 ERROR app.log` | Context trước/sau lỗi |

## Bước 3: Bảng giả thuyết

Mỗi giả thuyết ghi: mô tả, evidence ủng hộ, evidence phản bác, cách kiểm chứng, xác suất ban đầu.
Ví dụ thật: lỗi `KeyError: 'user'` sau commit refactor:
- H1: field bị rename trong migration (prob 60%) → check migration file
- H2: cache trả data cũ schema (prob 30%) → clear cache, rerun
- H3: API ngoài trả format khác (prob 10%) → inspect response raw

## Bước 5: Reproducer criteria

Reproducer đạt chuẩn khi: (a) chạy độc lập không cần setup đầy đủ, (b) fail 100% lần chạy, (c) nhỏ nhất có thể (≤50 dòng khuyến nghị).
""")

w("deep-debugger", "HYPOTHESIS-TEMPLATE.md", """# Hypothesis Table Template

| # | Hypothesis | Evidence ủng hộ | Evidence phản bác | Cách kiểm chứng | Xác suất | Kết quả |
|---|-----------|-----------------|-------------------|------------------|----------|---------|
| 1 | | | | | % | PROVEN/REJECTED |
| 2 | | | | | % | |
| 3 | | | | | % | |

Rule: tổng xác suất = 100%; không đóng bảng khi chưa có 1 PROVEN; REJECTED phải có lý do ghi trong "Kết quả".
""")

# ---------------------------------------------------------------- test-engineer
w("test-engineer", "COVERAGE-GUIDE.md", """# Coverage Guide

## Cách đo coverage thật

```bash
python3 -m pytest --cov=src --cov-report=term-missing --cov-branch
```

Không tin coverage ước lượng bằng mắt. Report `term-missing` cho biết CHÍNH XÁC dòng nào chưa chạy — dùng nó làm input cho bước generate tests.

## Viết test cho uncovered path — priority order

1. Error paths (raise/except) chưa có test
2. Branch chưa chạy (missing lines trong report)
3. Boundary values (0, -1, max, empty collection)
4. Happy path chính

## Anti-patterns

- Test chỉ cover dòng mà không assert gì hữu ích → coverage xanh, chất lượng đỏ
- Mock quá nhiều → test không catch bug integration
- Test phụ thuộc thứ tự chạy → flaky
""")

w("test-engineer", "MUTATION-REFERENCE.md", """# Mutation Testing Reference

## Nguyên lý

Mutant = thay đổi nhỏ code (toán tử, hằng số, điều kiện). Test suite mạnh phải làm test FAIL khi có mutant → "kill". Mutant sống sót (survive) = test suite KHÔNG phát hiện thay đổi đó → blind spot.

## Operators phổ biến

| Operator | Thay đổi | Ví dụ |
|----------|----------|-------|
| AOR | `+` → `-`, `*` → `/` | `a + b` → `a - b` |
| ROR | `>` → `>=`, `==` → `!=` | `if x > 0` → `if x >= 0` |
| UOI | `i++` → `i--` | vòng lặp |
| LCR | `&&` → `or` | `a and b` → `a or b` |
| SDL | xóa statement | xóa dòng assign |

## Metric

mutation score = killed / total (không tính equivalent mutants). Target ≥ 70%.
Equivalent mutant (code thay đổi nhưng behavior giữ nguyên) phải mark manual, không count.
""")

# ---------------------------------------------------------------- dependency-doctor
w("dependency-doctor", "ECOSYSTEMS.md", """# Ecosystem Specifics

## pip (requirements.txt / pyproject.toml)

Manifest: `requirements.txt`, `setup.py`, `pyproject.toml`. Lockfile: `requirements-lock.txt` (không bắt buộc). Cài `uv pip compile` để có lockfile. Check outdated: parse version specifiers so registry khi online; offline dùng heuristic pattern (year-old versions).

## npm (package.json)

Manifest: `package.json` + `package-lock.json`. Lockfile BẮT BUỘC có để audit đúng version. Check: `npm outdated` (online) hoặc parse lockfile trực tiếp. Workspace: đọc `workspaces` field.

## cargo (Rust)

Manifest: `Cargo.toml` + `Cargo.lock`. Check: parse `Cargo.lock`精确 version, so embedded CVE list. `cargo tree -d` tìm duplicate.

## go (go.mod)

Manifest: `go.mod` + `go.sum`. Check: parse `go.mod` require blocks. `go mod tidy` check consistency.

## Nguyên tắc chung

Lockfile là source of truth về version install thật; manifest chỉ là intent.
""")

w("dependency-doctor", "CVE-LIMITATIONS.md", """# CVE Database Limitations

`references/cves.json` là embedded CVE list curated — KHÔNG phải database đầy đủ.

Giới hạn đã biết: (1) chỉ cover CVE phổ biến của package major, (2) cập nhật theo release cycle của skill, (3) CVE mới trong 30 ngày có thể thiếu.

Chế độ offline: chỉ dùng embedded list, report ghi rõ `offline_mode: true`.
Chế độ online (permission network: outbound-only): bổ sung query registry API công khai (PyPI simple index, npm registry) để lấy version mới nhất — vẫn KHÔNG auto-upgrade.

Không bao giờ claim "100% safe" — chỉ claim "không phát hiện vấn đề đã biết trong database hiện có".
""")

# ---------------------------------------------------------------- performance-engineer
w("performance-engineer", "PROFILING-TOOLS.md", """# Profiling Tools Reference

## Python

| Tool | Use when | Command |
|------|----------|---------|
| `time.perf_counter` | đo 1 function đơn | manual wrapper |
| `cProfile` | tìm hot function trong program | `python3 -m cProfile -s cumtime script.py` |
| `line_profiler` | tìm hot line trong 1 function | `kernprof -l` |
| `timeit` | so micro-benchmark | `python3 -m timeit` |
| `memray`/`tracemalloc` | memory leak/profile | `python3 -m memray run` |

## Quy tắc đo

- Warmup ≥ 1 lần trước khi đo chính thức
- Iterations ≥ 5, report median + p95
- Cùng machine, cùng environment cho before/after
- Đo production-like workload, không synthetic quá đơn giản
""")

w("performance-engineer", "STATS-NOTES.md", """# Statistical Notes

## Vì sao median thay vì mean

Mean nhạy outlier: 1 lần GC pause 200ms giữa 5 lần đo 10ms → mean 52ms, median 10ms. Median phản ánh "trường hợp điển hình" tốt hơn cho performance.

## Outlier handling

Loại bỏ iteration đầu (warmup effect). Không loại thêm iteration khác trừ khi có lý do ghi lại (VD: background process spike — phải ghi evidence).

## Significance threshold

Speedup ≥ 20% mới coi đáng kể (dưới ngưỡng này nằm trong noise đo lường thông thường). Luôn verify correctness sau patch: output before == output after.
""")

# ---------------------------------------------------------------- refactor-engineer
w("refactor-engineer", "SMELL-CATALOG.md", """# Smell Catalog + Thresholds

| Smell | Detection | Threshold mặc định | Severity |
|-------|-----------|--------------------|----------|
| God class | class > 500 dòng HOẶC > 15 methods HOẶC > 10 public attributes | vượt 1 trong 3 | HIGH |
| Long function | > 50 dòng HOẶC nested > 4 levels | vượt 1 trong 2 | MEDIUM |
| Duplication | clone detection (normalized hash) đoạn ≥ 6 dòng trùng | ≥ 2 occurrences | MEDIUM |
| Circular dependency | cycle trong import graph (DFS) | ≥ 1 cycle | HIGH |
| Deep inheritance | hierarchy depth > 4 | depth > 4 | MEDIUM |
| Shotgun surgery | 1 change cần sửa > 5 files | pattern trong git history | HIGH |
| Feature envy | method dùng attributes class khác nhiều hơn class mình | heuristic count | LOW |

Ngưỡng có thể override qua `--thresholds FILE` (JSON). Threshold chỉ là signal — AI quyết định cuối dựa context.
""")

w("refactor-engineer", "SAFETY-CHECKLIST.md", """# Refactor Safety Checklist

Trước khi refactor:
- [ ] Regression suite chạy và GREEN
- [ ] Characterization test viết cho behavior quan trọng (nếu chưa có test)
- [ ] Đã commit trạng thái hiện tại

Trong khi refactor:
- [ ] Mỗi bước nhỏ (≤ 1 smell, ≤ 50 dòng thay đổi)
- [ ] Regression chạy sau MỖI bước
- [ ] Commit riêng từng bước với message mô tả

Sau khi refactor:
- [ ] Regression suite GREEN
- [ ] Behavior entry points không đổi (verify output)
- [ ] Smell detector re-run: smell giảm
- [ ] Không có smell MỚI sinh ra
""")

# ---------------------------------------------------------------- codebase-architect
w("codebase-architect", "METRICS-DEFINITIONS.md", """# Architecture Metrics Definitions

## Ca (Afferent Coupling)

Số module KHÁC import module X. Ca cao = module được nhiều nơi phụ thuộc = hotspot, thay đổi rủi ro cao.

## Ce (Efferent Coupling)

Số module X import. Ce cao = module phụ thuộc nhiều thứ = dễ break khi dependency đổi.

## I (Instability) = Ce / (Ca + Ce)

I ≈ 0: stable (khó thay đổi), I ≈ 1: unstable (dễ thay đổi). Module abstract nên stable; module concrete chi tiết nên unstable.

## Hotspot score

hotspot = Ca cao + recently changed (git log 90 ngày). Module vừa hot vừa stable-heavy là priority refactor candidate.

## Cycle

Cycle trong import graph = coupling vòng tròn; phá vòng bằng dependency inversion (interface ở module common).
""")

w("codebase-architect", "DIAGRAM-RULES.md", """# Diagram Generation Rules

1. Diagram Mermaid sinh TỰ ĐỘNG từ graph.json thật — không vẽ tay.
2. Validate roundtrip: parse diagram output phải reconstruct được graph gốc (test bằng `scripts/verify_diagram.py`).
3. Module > 1 file gom thành 1 node; dependency aggregation bằng số import.
4. Edge label = số dependency giữa 2 module.
5. Cycle highlight bằng stroke màu đỏ + ghi chú "CYCLE".
6. Giới hạn diagram ≤ 30 nodes; module nhỏ gom vào "others" cluster.
""")

# ---------------------------------------------------------------- repo-resurrection
w("repo-resurrection", "AUDIT-CHECKLIST.md", """# Repo State Audit Checklist

| # | Item | Check command | Pass criteria |
|---|------|---------------|---------------|
| 1 | Last commit age | `git log -1 --format=%ci` | ghi nhận, > 1 năm = legacy flag |
| 2 | Build broken? | chạy build command trong docs/CI | exit 0 |
| 3 | Tests status | chạy test suite | ≥ 1 suite chạy được |
| 4 | Dependency freshness | so manifest version vs registry | ghi tuổi từng dep |
| 5 | Docs dead links | scan README/docs links | internal links tồn tại |
| 6 | CI config hiện hữu? | `.github/`, `.travis.yml`, `ci/` | ghi nhận |
| 7 | Runtime version | toolchain version yêu cầu vs hiện tại | tương thích |
| 8 | Secret scan nhanh | scan pattern secrets trong repo | 0 secret thật |
""")

w("repo-resurrection", "MODERNIZATION-GUIDE.md", """# Modernization Guide — what is IN scope vs OUT

## IN scope (được phép)

- Dependency version fix để build/test pass
- Security patch dependencies
- Toolchain version update nếu bắt buộc
- Doc generation từ code hiện tại
- CI skeleton (chạy test)

## OUT of scope (KHÔNG làm nếu không được yêu cầu explicit)

- Rewrite ngôn ngữ/framework
- Đổi kiến trúc
- Feature mới
- Reformat toàn repo (format chỉ file chạm tới)

## Decision log format

Mỗi decision quan trọng ghi: `DECISION: <what> — RATIONALE: <why> — ALTERNATIVES: <what else considered>`.
Decision log nằm trong `docs/decisions/` của repo được hồi sinh.
""")

# ---------------------------------------------------------------- release-engineer
w("release-engineer", "CHECKLIST-REFERENCE.md", """# Release Checklist Reference

| # | Item | Check cách | Evidence |
|---|------|------------|----------|
| 1 | CHANGELOG entry version mới | grep CHANGELOG "## [<version>]" | line match |
| 2 | Version bump nhất quán | metadata == git tag == CHANGELOG | 3 giá trị bằng nhau |
| 3 | Tests pass | chạy test suite repo | exit 0 + count |
| 4 | Build artifact tạo được | `python3 -m build` / `npm pack` | file tồn tại |
| 5 | LICENSE tồn tại | file check | tồn tại |
| 6 | Artifact không chứa file nhạy cảm | secret scan artifact | 0 match |
| 7 | Binary không trong source dist | list artifact contents | không có .so/.exe |
| 8 | README đề cập version mới | grep | line match |

Item nào không áp dụng được (VD: repo chưa có CI) ghi `NA` với lý do, KHÔNG bỏ qua silent.
""")

w("release-engineer", "SEMVER-GUIDE.md", """# Semver Guide (2.0.0)

Format: MAJOR.MINOR.PATCH.

- **MAJOR** bump: breaking change API/hành vi (user code hiện tại break)
- **MINOR** bump: feature mới backward-compatible
- **PATCH** bump: bugfix backward-compatible

Nguyên tắc release engineer: đọc diff từ tag trước → phân loại breaking/non-breaking → đề xuất bump level + giải thích. Không tự quyết định MAJOR bump một mình — luôn đưa đề xuất kèm rationale cho người quyết định.
Pre-release: `-alpha.1`, `-beta.2` theo semver spec.
""")

# ---------------------------------------------------------------- documentation-engineer
w("documentation-engineer", "STYLE-GUIDE.md", """# Documentation Style Guide

1. Heading: ATX style (#, ##, ###), không跳过 level.
2. Code fence luôn có language: ```python, ```bash.
3. Table: pipe syntax, header + separator bắt buộc.
4. Links: relative path cho internal, tuyệt đối https cho external.
5. Câu hoàn chỉnh, thì hiện tại, voice chủ động.
6. Thuật ngữ nhất quán: chọn 1 term (VD: "module" không đổi sang "package" giữa文档).
7. Mỗi trang có 1 chủ đề chính; liên kết chéo thay vì trang dài.
""")

w("documentation-engineer", "EXAMPLE-RULES.md", """# Runnable Example Rules

1. Mọi code block dạng instruction (không phải illustration) phải chạy được khi copy-paste.
2. Example bao gồm: setup (nếu cần), action, expected output comment.
3. Nếu example cần fixture: script tạo fixture inline hoặc trỏ fixture có sẵn trong repo.
4. Example không dùng placeholder cần thay thế ([YOUR_TOKEN]) trừ khi docs dạy cấu hình — khi đó ghi rõ bắt buộc thay.
5. Verify: `scripts/check_examples.py` chạy mọi code block, exit code 0 = pass.
6. Example cũ hơn code = example sai: khi code đổi behavior, example phải update cùng commit.
""")

print("references created for all 9 skills")
