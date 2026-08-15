"""AgentSkillsLab shared constants and error types."""

from __future__ import annotations

import enum
import re

# ---------------------------------------------------------------- constants

SPEC_VERSION = "1.0"

SKILL_DIR_RESERVED_NAMES = {
    "anthropic",
    "claude",
    "manus",
    "openai",
    "agentskillslab",
}

NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
SEMVER_PATTERN = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$"
)
DESCRIPTION_MIN_LENGTH = 30

# Giới hạn an toàn (thiết kế chống resource exhaustion — T8)
MAX_FRONTMATTER_KB = 64          # 64 KiB max cho YAML frontmatter
MAX_SKILL_FILE_KB = 500          # 500 KiB max cho SKILL.md
MAX_MANIFEST_KB = 100            # 100 KiB max cho skill.yaml
MAX_TOTAL_DIR_MB = 100           # 100 MiB max tổng skill dir khi validate
MAX_SYMLINK_DEPTH = 8
MAX_INDEXED_SKILLS_WARN = 10_000

# File nhị phân / thực thi cấm trong skill dir (V-012, V-022)
FORBIDDEN_EXTENSIONS = {
    ".exe", ".dll", ".so", ".dylib", ".bat", ".cmd", ".com", ".msi",
}

# Extensions được phép trong scripts/
ALLOWED_SCRIPT_EXTENSIONS = {".py", ".sh", ".js", ".ts", ".rb", ".go", ".pl"}

SPDX_LICENSES = {
    "MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "MPL-2.0",
    "GPL-2.0-only", "GPL-3.0-only", "LGPL-2.1-only", "LGPL-3.0-only",
    "AGPL-3.0-only", "Unlicense", "0BSD", "BlueOak-1.0.0", "Artistic-2.0",
    "Zlib", "BSL-1.0", "CC0-1.0", "CC-BY-4.0", "CC-BY-SA-4.0",
    "ECL-2.0", "EUPL-1.2", "MIT-0", "MulanPSL-2.0", "PostgreSQL",
    "Ruby", "SIL-OFL-1.1", "UPL-1.0", "WTFPL", "X11", "Vim",
}

SUPPORTED_AGENTS = [
    "claude-code",
    "codex",
    "cursor",
    "github-copilot",
    "opencode",
    "kilo",
    "cline",
    "aider",
    "vscode-agent",
    "manus",
]


# ---------------------------------------------------------------- exit codes

class ExitCode(enum.IntEnum):
    OK = 0
    VALIDATION_FAILED = 2
    RUNTIME_ERROR = 3
    SECURITY_VIOLATION = 4
    NOT_FOUND = 5
    PERMISSION_DENIED = 6
    TIMEOUT = 7
    USAGE_ERROR = 64


class Exit(Exception):
    """Raise to terminate CLI with a specific exit code and message."""

    def __init__(self, code: ExitCode, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


# ---------------------------------------------------------------- utilities

def kb(bytes_: int) -> int:
    return bytes_ // 1024


def human_size(bytes_: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if abs(bytes_) < 1024:
            return f"{bytes_:.1f} {unit}"
        bytes_ /= 1024  # type: ignore[assignment]
    return f"{bytes_:.1f} TB"
