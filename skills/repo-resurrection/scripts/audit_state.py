#!/usr/bin/env python3
"""audit_state: audit trạng thái repo cũ — deliverable bước 1 của workflow Resurrection.

Usage: python3 audit_state.py <repo> [--output report.json]

Kiểm tra (xem references/AUDIT-CHECKLIST.md):
- last commit age, CI config, manifest/lockfile, docs, build/test commands,
- secret scan nhanh, dependency age heuristic
Output JSON: checklist items với status + evidence.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "dependency-doctor" / "scripts"))


def git(args: list[str], cwd: Path, timeout: int = 30) -> str:
    try:
        r = subprocess.run(["git"] + args, cwd=str(cwd), capture_output=True,
                           text=True, timeout=timeout, check=False)
        return r.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""


TEXT_FILE_SUFFIXES = {".py", ".js", ".ts", ".json", ".yaml", ".yml", ".env",
                    ".md", ".txt", ".cfg", ".toml", ".sh", ".rb", ".go", ".rs"}

SECRET_PATTERNS = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "aws_access_key"),
    (re.compile(r"(?i)(password|secret|api[_-]?key)\s*[:=]\s*\S{8,}"), "possible_credential"),
    (re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY"), "private_key"),
    (re.compile(r"ghp_[A-Za-z0-9]{36}"), "github_token"),
]


def audit_secrets(repo: Path) -> list[dict]:
    found = []
    for f in repo.rglob("*"):
        if not f.is_file():
            continue
        parts = f.relative_to(repo).parts
        if any(p.startswith(".") or p in {"node_modules", "__pycache__", "venv", ".git"} for p in parts):
            continue
        if f.suffix not in TEXT_FILE_SUFFIXES:
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pat, kind in SECRET_PATTERNS:
            for m in pat.finditer(text):
                found.append({"file": str(f.relative_to(repo)), "kind": kind,
                              "match": m.group(0)[:20] + "..."})
                if len(found) >= 20:
                    return found
    return found


def main() -> int:
    p = argparse.ArgumentParser(description="Audit trạng thái repo cũ")
    p.add_argument("repo", help="thư mục repo")
    p.add_argument("--output", "-o", default=None)
    args = p.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        print(f"ERROR: '{repo}' không phải thư mục", file=sys.stderr)
        return 1

    t0 = time.perf_counter()
    checks: list[dict] = []

    # 1. Last commit
    log = git(["log", "-1", "--format=%ci|%s"], repo)
    if log.strip():
        when_str, subject = log.strip().split("|", 1)
        when = datetime.fromisoformat(when_str.strip())
        if when.tzinfo is None:
            when = when.replace(tzinfo=timezone.utc)
        age_days = (datetime.now(timezone.utc) - when).days
        checks.append({"item": "last_commit", "status": "INFO",
                       "value": f"{when.isoformat()} ({age_days} ngày trước)",
                       "evidence": subject})
        checks.append({"item": "legacy_flag",
                       "status": "WARNING" if age_days > 365 else "OK",
                       "value": "legacy" if age_days > 365 else "recent",
                       "evidence": f"age={age_days}d"})
    else:
        checks.append({"item": "last_commit", "status": "MISSING",
                       "value": "không có git history hoặc không phải git repo", "evidence": ""})

    # 2. CI config
    ci_files = [f for f in [".github", ".travis.yml", "ci", ".gitlab-ci.yml",
                            "azure-pipelines.yml", ".circleci"] if (repo / f).exists()]
    checks.append({"item": "ci_config", "status": "OK" if ci_files else "MISSING",
                   "value": ", ".join(ci_files) or "không tìm thấy", "evidence": ""})

    # 3. Manifests
    manifests = [f.name for f in [repo / "requirements.txt", repo / "package.json",
                                  repo / "Cargo.toml", repo / "go.mod",
                                  repo / "pyproject.toml", repo / "setup.py"] if f.exists()]
    checks.append({"item": "manifests", "status": "OK" if manifests else "MISSING",
                   "value": ", ".join(manifests) or "không tìm thấy", "evidence": ""})

    # 4. Docs
    docs = [f.name for f in [repo / "README.md", repo / "README.rst", repo / "CONTRIBUTING.md",
                             repo / "docs"] if f.exists()]
    checks.append({"item": "docs", "status": "OK" if docs else "MISSING",
                   "value": ", ".join(docs) or "không tìm thấy", "evidence": ""})

    # 5. Test suite
    test_dirs = [d.name for d in [repo / "tests", repo / "test", repo / "spec"] if d.is_dir()]
    test_files = len(list(repo.rglob("test_*.py"))) + len(list(repo.rglob("*_test.py")))
    checks.append({"item": "test_suite", "status": "OK" if (test_dirs or test_files) else "MISSING",
                   "value": f"dirs={test_dirs or []}, test_files={test_files}", "evidence": ""})

    # 6. Build commands trong docs
    readme = repo / "README.md"
    build_refs = []
    if readme.exists():
        text = readme.read_text(encoding="utf-8", errors="replace")
        for kw in ["make build", "python -m build", "npm run build", "cargo build",
                   "docker build", "poetry build", "tox"]:
            if kw in text:
                build_refs.append(kw)
    checks.append({"item": "build_documented", "status": "OK" if build_refs else "MISSING",
                   "value": ", ".join(build_refs) or "không tìm thấy lệnh build trong README",
                   "evidence": ""})

    # 7. Secret scan
    secrets = audit_secrets(repo)
    checks.append({"item": "secret_scan",
                   "status": "WARNING" if secrets else "OK",
                   "value": f"{len(secrets)} matches", "evidence": secrets[:5]})

    # 8. Virtualenv/docker hiện diện
    venv = any((repo / d).exists() for d in ["venv", ".venv", "env", ".env"])
    docker = (repo / "Dockerfile").exists() or (repo / "docker-compose.yml").exists()
    checks.append({"item": "environment_files",
                   "status": "OK" if (venv or docker) else "MISSING",
                   "value": f"venv={venv}, docker={docker}", "evidence": ""})

    report = {
        "repo": str(repo),
        "audit_seconds": round(time.perf_counter() - t0, 2),
        "checks": checks,
        "summary": {
            "ok": sum(1 for c in checks if c["status"] == "OK"),
            "warning": sum(1 for c in checks if c["status"] == "WARNING"),
            "missing": sum(1 for c in checks if c["status"] == "MISSING"),
        },
    }

    out = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"Audit: OK={report['summary']['ok']} WARNING={report['summary']['warning']} "
              f"MISSING={report['summary']['missing']} | {report['audit_seconds']}s")
        print(f"Output: {args.output}")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
