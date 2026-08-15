#!/usr/bin/env python3
"""collect_context: trích context debugging từ repo.

Usage: python3 collect_context.py <repo> [--log LOG_FILE] [--output context.json]

Output JSON gồm: git_log (5 commits gần nhất với stats), changed_files
(files sửa trong 5 commit gần), environment, log_tail (nếu --log).
Không invent context: mọi dữ liệu từ git/log thật.
"""
from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
from pathlib import Path


def git(args: list[str], cwd: Path, timeout: int = 60) -> str:
    try:
        r = subprocess.run(["git"] + args, cwd=str(cwd), capture_output=True,
                           text=True, timeout=timeout, check=False)
        return r.stdout
    except FileNotFoundError:
        return ""
    except subprocess.TimeoutExpired:
        return ""


def main() -> int:
    p = argparse.ArgumentParser(description="Thu thập context debugging từ repo")
    p.add_argument("repo", help="thư mục repo")
    p.add_argument("--log", default=None, help="file log cần trích tail")
    p.add_argument("--output", "-o", default=None)
    args = p.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        print(f"ERROR: '{repo}' không phải thư mục", file=sys.stderr)
        return 1

    context: dict = {
        "repo": str(repo),
        "environment": {
            "os": platform.system(),
            "python": sys.version.split()[0],
            "cwd_files": sorted([f.name for f in repo.iterdir()])[:50],
        },
        "git_available": bool(subprocess.run(["git", "version"],
                                             capture_output=True, timeout=10).returncode == 0),
        "git_log": [],
        "recently_changed_files": [],
        "log_tail": None,
        "warnings": [],
    }

    if context["git_available"]:
        log_out = git(["log", "-5", "--format=%h|%ad|%an|%s", "--date=short"], repo)
        for line in log_out.strip().splitlines():
            parts = line.split("|", 3)
            if len(parts) == 4:
                context["git_log"].append({
                    "commit": parts[0], "date": parts[1],
                    "author": parts[2], "subject": parts[3],
                })

        changed = git(["diff", "--name-only", "HEAD~5", "HEAD"], repo)
        context["recently_changed_files"] = [f for f in changed.strip().splitlines() if f]

        stat_out = git(["log", "-5", "--shortstat", "--format="], repo)
        context["git_diff_stat"] = stat_out.strip()

        if not log_out.strip():
            context["warnings"].append(
                "không đọc được git history — có thể không phải git repo")
    else:
        context["warnings"].append("git không khả dụng — context giới hạn")

    if args.log:
        log_path = Path(args.log).resolve()
        if log_path.is_file():
            try:
                tail = log_path.read_text(encoding="utf-8", errors="replace").splitlines()[-50:]
                context["log_tail"] = tail
            except OSError as exc:
                context["warnings"].append(f"không đọc được log: {exc}")
        else:
            context["warnings"].append(f"file log không tồn tại: {log_path}")

    out = json.dumps(context, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"Context lưu tại {args.output}")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
