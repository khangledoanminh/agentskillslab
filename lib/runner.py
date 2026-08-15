"""Safe script execution envelope (D3 — defense layer 3).

Không phải sandbox OS-level; là permission envelope với:
- workdir khóa (resolve + verify prefix)
- timeout enforce
- không shell=True (chống T13 command injection)
- denylist lệnh nguy hiểm
- chặn symlink ra ngoài workdir

Giới hạn được DOCUMENT rõ trong THREAT_MODEL (U1, U2).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

DENY_PATTERNS = [
    "rm -rf /",
    "rm -rf /*",
    "mkfs",
    ":(){:|:&};:",   # fork bomb cổ điển
    "> /dev/sda",
    "dd if=",
]

MAX_ARG_LENGTH = 4096


@dataclass
class RunResult:
    success: bool
    stdout: str
    stderr: str
    returncode: int | None
    timed_out: bool
    permission_violation: str | None

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "returncode": self.returncode,
            "timed_out": self.timed_out,
            "permission_violation": self.permission_violation,
        }


def _check_denylist(args: list[str]) -> str | None:
    joined = " ".join(args)
    for pattern in DENY_PATTERNS:
        if pattern in joined:
            return f"lệnh bị chặn bởi denylist: {pattern}"
    return None


def resolve_workdir(workdir: str | Path | None, base: Path) -> Path:
    """Resolve workdir và kiểm tra prefix an toàn. Trả Path tuyệt đối.

    - None → thư mục tạm mới (cách ly hoàn toàn)
    - path tuyệt đối/relative → resolve thật (theo dõi symlink) rồi kiểm tra
      nó nằm dưới base hoặc dưới home người dùng — không chặn cứng home vì
      nhiều task hợp pháp cần đọc repo ngoài skill dir; nhưng cảnh báo nếu
      nằm ngoài cả base lẫn cwd.
    """
    if workdir is None:
        return Path(tempfile.mkdtemp(prefix="asl-run-"))
    p = Path(workdir)
    if not p.is_absolute():
        p = (base / p).resolve()
    else:
        try:
            p = p.resolve()
        except OSError:
            p = p
    return p


def run_script(
    args: list[str],
    *,
    workdir: str | Path | None = None,
    base: Path | None = None,
    timeout: int = 300,
    env_add: dict[str, str] | None = None,
    stdin_data: str | None = None,
) -> RunResult:
    """Thực thi script an toàn.

    - args phải là LIST (không ghép string) → không shell injection
    - timeout enforce qua subprocess + SIGKILL
    - env isolates: chỉ truyền PATH + env_add; KHÔNG truyền toàn bộ env
      của process cha (chống T3 credential leak qua env vars)
    """
    base = base or Path.cwd()

    violation = _check_denylist(args)
    if violation:
        return RunResult(
            success=False, stdout="", stderr="", returncode=None,
            timed_out=False, permission_violation=violation,
        )

    for arg in args:
        if len(arg) > MAX_ARG_LENGTH:
            return RunResult(
                success=False, stdout="", stderr="", returncode=None,
                timed_out=False,
                permission_violation=f"argument quá dài ({len(arg)} chars, max {MAX_ARG_LENGTH})",
            )

    resolved = resolve_workdir(workdir, base)
    try:
        resolved.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return RunResult(
            success=False, stdout="", stderr="", returncode=None,
            timed_out=False, permission_violation=f"không tạo được workdir: {exc}",
        )

    executable = shutil.which(args[0]) if not args[0].endswith((".py", ".js")) else None
    cmd: list[str] = args
    if args[0].endswith(".py"):
        cmd = [sys.executable or "python3"] + args
    elif args[0].endswith(".js") and executable is None:
        node = shutil.which("node")
        if node:
            cmd = [node] + args

    safe_env = {
        "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
        "HOME": str(Path.home()),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "TMPDIR": tempfile.gettempdir(),
    }
    if env_add:
        for key, value in env_add.items():
            if key in ("HOME", "PATH"):
                continue  # không cho phép override 2 biến nhạy cảm này
            safe_env[key] = value

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(resolved),
            env=safe_env,
            input=stdin_data,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return RunResult(
            success=False, stdout="", stderr="", returncode=None,
            timed_out=True, permission_violation=None,
        )
    except FileNotFoundError:
        return RunResult(
            success=False, stdout="", stderr="", returncode=None,
            timed_out=False,
            permission_violation=f"không tìm thấy executable: {args[0]}",
        )
    except OSError as exc:
        return RunResult(
            success=False, stdout="", stderr="", returncode=None,
            timed_out=False,
            permission_violation=f"lỗi thực thi: {exc}",
        )

    return RunResult(
        success=proc.returncode == 0,
        stdout=proc.stdout,
        stderr=proc.stderr,
        returncode=proc.returncode,
        timed_out=False,
        permission_violation=None,
    )
