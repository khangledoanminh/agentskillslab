#!/usr/bin/env python3
"""agent-skills — CLI quản lý AgentSkillsLab Skills.

Commands:
  validate   <dir>           Validate một hoặc nhiều skill dirs
  test       <skill-dir>     Chạy test suite của skill
  benchmark  <skill-dir>     Chạy benchmarks của skill (hoặc project)
  inspect    <skill-dir>     Hiển thị metadata skill
  search     <query>         Tìm skill trong skill roots
  doctor                      Kiểm tra môi trường (requirements, commands)
  version                     In phiên bản CLI + spec

Exit codes: xem lib/common.py ExitCode.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from lib.common import ExitCode, SPEC_VERSION  # noqa: E402
from lib.index import Index  # noqa: E402
from lib.manifest import parse_frontmatter, parse_manifest  # noqa: E402
from lib.runner import run_script  # noqa: E402
from lib.validator import validate_skill  # noqa: E402
from lib.benchmarks import environment_info  # noqa: E402

CLI_VERSION = "1.0.0"
DEFAULT_SKILL_ROOTS = [PROJECT_ROOT / "skills"]


def cmd_validate(args: argparse.Namespace) -> int:
    targets = [Path(p) for p in args.targets]
    if not targets:
        targets = [d for d in DEFAULT_SKILL_ROOTS if d.is_dir()]

    def expand(target: Path) -> list[Path]:
        """Nếu target là thư mục chứa nhiều skill dirs con, mở rộng thành từng skill dir."""
        if not target.is_dir():
            return [target]
        skill_md = target / "SKILL.md"
        if skill_md.exists():
            return [target]
        kids = [d for d in sorted(target.iterdir()) if d.is_dir() and not d.name.startswith(".")]
        if kids:
            return kids
        return [target]

    expanded: list[Path] = []
    for target in targets:
        expanded.extend(expand(target))
    overall = True
    for target in expanded:
        if not target.exists():
            print(f"ERROR: không tìm thấy '{target}'", file=sys.stderr)
            overall = False
            continue
        if target.is_file():
            # chấp nhận chỉ tới file SKILL.md → dùng thư mục cha
            if target.name == "SKILL.md":
                target = target.parent
            else:
                print(f"ERROR: '{target}' không phải skill dir hay SKILL.md", file=sys.stderr)
                overall = False
                continue
        t0 = time.perf_counter()
        report = validate_skill(target)
        elapsed = time.perf_counter() - t0
        print(f"== {target.name} {'PASS' if report.passed else 'FAIL'} "
              f"({len(report.errors)} lỗi, {len(report.warnings)} cảnh báo, {len(report.infos)} info, {elapsed*1000:.0f}ms)")
        for f_ in report.findings:
            print(f"   {f_}")
        if report.security_findings:
            print(f"   -- security scan: {len(report.security_findings)} findings")
            for sf in report.security_findings:
                print(f"      [{sf.severity}] {sf.rule_id} {sf.file}:{sf.line} — {sf.evidence}")
        if not report.passed:
            overall = False
    return ExitCode.OK if overall else ExitCode.VALIDATION_FAILED


def cmd_test(args: argparse.Namespace) -> int:
    skill_dir = Path(args.skill_dir).resolve()
    tests_dir = skill_dir / "tests"
    if not tests_dir.is_dir():
        print(f"ERROR: '{skill_dir.name}' không có thư mục tests/", file=sys.stderr)
        return ExitCode.NOT_FOUND

    runner_files = sorted(
        [f for f in tests_dir.rglob("*") if f.is_file() and not f.is_symlink()
         and f.suffix in (".py", ".sh")]
    )
    if not runner_files:
        print("ERROR: không tìm thấy file test (.py/.sh) trong tests/", file=sys.stderr)
        return ExitCode.NOT_FOUND

    passed = 0
    failed = 0
    results: list[dict] = []
    for runner in runner_files:
        rel = runner.relative_to(tests_dir)
        timeout = args.timeout
        result = run_script(
            [str(runner)], workdir=str(skill_dir), base=skill_dir, timeout=timeout,
        )
        ok = result.success and result.permission_violation is None
        results.append({
            "test": str(rel),
            "pass": ok,
            "returncode": result.returncode,
            "timed_out": result.timed_out,
            "permission_violation": result.permission_violation,
            "stdout_tail": result.stdout[-2000:],
            "stderr_tail": result.stderr[-2000:],
        })
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] tests/{rel}" +
              (f" — {result.permission_violation}" if result.permission_violation else "") +
              (f" — timed out after {timeout}s" if result.timed_out else ""))
        if not ok:
            if result.stdout_tail.strip():
                print("    stdout:", result.stdout_tail.strip().replace("\n", "\n    ")[:800])
            if result.stderr_tail.strip():
                print("    stderr:", result.stderr_tail.strip().replace("\n", "\n    ")[:800])
        if ok:
            passed += 1
        else:
            failed += 1

    total = passed + failed
    print(f"\nTest results: {total} total, {passed} passed, {failed} failed")
    if args.json:
        print(json.dumps({"skill": skill_dir.name, "passed": passed,
                          "failed": failed, "results": results}, indent=2))
    return ExitCode.OK if failed == 0 else ExitCode.VALIDATION_FAILED


def cmd_benchmark(args: argparse.Namespace) -> int:
    target = Path(args.skill_dir).resolve()
    bench_dir = target / "benchmarks" if target.is_dir() else None
    if bench_dir is None or not bench_dir.is_dir():
        print(f"ERROR: không tìm thấy benchmarks/ trong '{target}'", file=sys.stderr)
        return ExitCode.NOT_FOUND

    runners = sorted([f for f in bench_dir.rglob("*")
                      if f.is_file() and f.suffix in (".py", ".sh")])
    if not runners:
        print("ERROR: không có runner (.py/.sh) trong benchmarks/", file=sys.stderr)
        return ExitCode.NOT_FOUND

    print("Environment:", json.dumps(environment_info()))
    all_results = []
    for runner in runners:
        rel = runner.relative_to(bench_dir)
        t0 = time.perf_counter()
        result = run_script([str(runner)], workdir=str(target), base=target,
                            timeout=args.timeout)
        elapsed = time.perf_counter() - t0
        ok = result.success and result.permission_violation is None
        print(f"== benchmarks/{rel}: {'OK' if ok else 'FAIL'} ({elapsed:.1f}s tổng)")
        if result.stdout.strip():
            print(result.stdout.strip()[:3000])
        if result.stderr.strip():
            print("stderr:", result.stderr.strip()[:1000])
        all_results.append({"benchmark": str(rel), "pass": ok,
                            "wall_seconds": round(elapsed, 2),
                            "stdout": result.stdout, "stderr": result.stderr})
        if not ok:
            print(f"   (permission_violation={result.permission_violation}, timed_out={result.timed_out})")

    if args.json:
        print(json.dumps({"skill": target.name, "environment": environment_info(),
                          "results": all_results}, indent=2))
    failed = sum(1 for r in all_results if not r["pass"])
    return ExitCode.OK if failed == 0 else ExitCode.RUNTIME_ERROR


def cmd_inspect(args: argparse.Namespace) -> int:
    skill_dir = Path(args.skill_dir).resolve()
    fm, fm_error = parse_frontmatter(skill_dir / "SKILL.md")
    manifest, m_error = (parse_manifest(skill_dir / "skill.yaml")
                         if (skill_dir / "skill.yaml").exists() else (None, None))
    output = {
        "dir": str(skill_dir),
        "frontmatter": {"error": fm_error} if fm is None else
                       {"name": fm.name, "description": fm.description},
        "manifest": {"error": m_error} if manifest is None else manifest.raw,
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return ExitCode.OK


def cmd_search(args: argparse.Namespace) -> int:
    index = Index()
    warnings = index.build(DEFAULT_SKILL_ROOTS)
    if not index.entries:
        print("Không tìm thấy skill nào trong", DEFAULT_SKILL_ROOTS, file=sys.stderr)
        return ExitCode.NOT_FOUND
    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)

    query = " ".join(args.query)
    hits = index.search(query, top=args.top)
    if not hits:
        print(f"Không có skill khớp query '{query}'")
        print("\nSkills hiện có:")
        for e in index.entries:
            print(f"  {e.name} — {e.title}")
        return ExitCode.OK
    for score, e in hits:
        print(f"  [{score:.0%}] {e.name} — {e.title}")
        print(f"        {e.description[:150]}")
    return ExitCode.OK


def cmd_doctor(args: argparse.Namespace) -> int:
    """Kiểm tra môi trường: Python version, commands yêu cầu bởi các skill."""
    print(f"agent-skills CLI {CLI_VERSION} | spec {SPEC_VERSION}")
    print(f"Python {sys.version.split()[0]} ({sys.executable})")
    print(f"Platform {sys.platform}")

    needed = {"git", "bash", "node", "python3"}
    optional = {"cargo", "go", "gradle", "npm", "pip", "uv", "mypy", "ruff",
                "pytest", "bandit", "pyright", "shellcheck"}
    print("\nRequired commands:")
    missing_required: list[str] = []
    for cmd in sorted(needed):
        present = shutil.which(cmd) is not None
        print(f"  {cmd}: {'OK' if present else 'MISSING'}")
        if not present:
            missing_required.append(cmd)
    print("\nOptional commands (chỉ cần cho skill tương ứng):")
    for cmd in sorted(optional):
        present = shutil.which(cmd) is not None
        print(f"  {cmd}: {'OK' if present else 'không có'}")

    # kiểm tra pyyaml
    try:
        import yaml  # noqa: F401
        yaml_status = "OK (PyYAML)"
    except ImportError:
        yaml_status = "fallback parser thuần (an toàn nhưng giới hạn)"
    print(f"\nYAML: {yaml_status}")

    if missing_required:
        print(f"\nWARNING: thiếu commands bắt buộc: {', '.join(missing_required)}")
        return ExitCode.OK  # doctor chỉ báo cáo, không fail
    print("\nDoctor: môi trường OK cho 4 skill foundation")
    return ExitCode.OK


def cmd_version(args: argparse.Namespace) -> int:
    print(f"agent-skills {CLI_VERSION}")
    print(f"Skill Specification {SPEC_VERSION}")
    print(f"Project root: {PROJECT_ROOT}")
    return ExitCode.OK


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="agent-skills",
        description="AgentSkillsLab CLI — validate, test, benchmark và quản lý Agent Skills",
    )
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("validate", help="Validate skill dirs theo SKILL_SPEC v1.0")
    sp.add_argument("targets", nargs="*", help="skill dirs (mặc định: tất cả trong skills/)")

    sp = sub.add_parser("test", help="Chạy test suite của skill")
    sp.add_argument("skill_dir", help="đường dẫn skill dir")
    sp.add_argument("--timeout", type=int, default=300, help="timeout mỗi test runner (giây)")
    sp.add_argument("--json", action="store_true", help="output JSON")

    sp = sub.add_parser("benchmark", help="Chạy benchmarks của skill")
    sp.add_argument("skill_dir", help="đường dẫn skill dir")
    sp.add_argument("--timeout", type=int, default=600, help="timeout mỗi runner (giây)")
    sp.add_argument("--json", action="store_true")

    sp = sub.add_parser("inspect", help="Hiển thị metadata skill")
    sp.add_argument("skill_dir", help="đường dẫn skill dir")

    sp = sub.add_parser("search", help="Tìm skill theo query")
    sp.add_argument("query", nargs="+", help="từ khóa tìm kiếm")
    sp.add_argument("--top", type=int, default=10)

    sub.add_parser("doctor", help="Kiểm tra môi trường và dependencies")
    sub.add_parser("version", help="In phiên bản")
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    dispatch = {
        "validate": cmd_validate,
        "test": cmd_test,
        "benchmark": cmd_benchmark,
        "inspect": cmd_inspect,
        "search": cmd_search,
        "doctor": cmd_doctor,
        "version": cmd_version,
    }
    try:
        return int(dispatch[args.command](args))
    except KeyError:
        parser.print_help()
        return ExitCode.USAGE_ERROR
    except Exception as exc:  # noqa: BLE001 — boundary an toàn, không crash silent
        print(f"FATAL: lỗi không xử lý được: {exc}", file=sys.stderr)
        return ExitCode.RUNTIME_ERROR


if __name__ == "__main__":
    sys.exit(main())
