#!/usr/bin/env python3
"""Security audit scanner — quét repo theo các rule SEC-001..SEC-006.

Usage: python3 audit.py <repo-root> [--output findings.json] [--exclude DIR,...]

Output JSON:
{
  "repo": "...",
  "scanned_files": N,
  "scan_seconds": F,
  "not_scanned": ["rule groups bị bỏ qua vì lý do"],
  "findings": [{"rule_id", "severity", "file", "line", "evidence", "why"}]
}

Không invent findings: chỉ báo cáo pattern khớp thực tế. Evidence của
secret được snip để tránh leak giá trị thật.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "__pycache__", ".venv", "venv",
    ".tox", ".mypy_cache", ".pytest_cache", "dist", "build", ".next",
    ".nuxt", "target", ".gradle", "bin", "obj", ".idea", ".vscode",
}

BINARY_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico", ".pdf",
    ".zip", ".gz", ".tar", ".bz2", ".xz", ".exe", ".dll", ".so", ".dylib",
    ".woff", ".woff2", ".ttf", ".otf", ".pyc", ".class", ".o", ".a", ".lib",
    ".db", ".sqlite", ".sqlite3", ".mp3", ".mp4", ".avi", ".mov", ".wasm",
}


def scan_repo(root: Path, exclude: set[str]) -> dict:
    findings = []
    scanned = 0
    t0 = time.perf_counter()
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS or part in exclude for part in rel.parts[:-1]):
            continue
        if path.suffix.lower() in BINARY_SUFFIXES:
            continue
        scanned += 1
        findings.extend(scan_file_local(path, rel))
    return {
        "repo": str(root),
        "scanned_files": scanned,
        "scan_seconds": round(time.perf_counter() - t0, 2),
        "not_scanned": [],
        "findings": [f.to_dict() for f in findings],
    }


def scan_file_local(path: Path, rel: Path):
    """Wrapper giữ rel path gốc thay vì chỉ tên file."""
    from lib.security import scan_file
    return scan_file(path, rel_root=str(rel.parent))


def main() -> int:
    p = argparse.ArgumentParser(description="Security audit scanner")
    p.add_argument("repo_root", help="thư mục gốc repo cần audit")
    p.add_argument("--output", "-o", default=None, help="file output JSON")
    p.add_argument("--exclude", default="", help="thư mục loại trừ, phân cách bằng dấu phẩy")
    args = p.parse_args()

    root = Path(args.repo_root).resolve()
    if not root.is_dir():
        print(f"ERROR: '{root}' không phải thư mục", file=sys.stderr)
        return 1

    exclude = {s.strip() for s in args.exclude.split(",") if s.strip()}
    result = scan_repo(root, exclude)

    out = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"Audit hoàn tất: {result['scanned_files']} files, "
              f"{len(result['findings'])} findings, {result['scan_seconds']}s")
        print(f"Output: {args.output}")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
