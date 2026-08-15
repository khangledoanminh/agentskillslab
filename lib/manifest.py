"""Manifest parsing: SKILL.md YAML frontmatter + skill.yaml.

Parser an toàn:
- Kích thước frontmatter/manifest giới hạn trước khi parse (chống YAML bomb — T11)
- SafeLoader nếu có yaml lib, parser thuần stdlib nếu không
- Mọi lỗi đều report dạng chẩn đoán, không crash.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .common import (
    MAX_FRONTMATTER_KB,
    MAX_MANIFEST_KB,
    MAX_SKILL_FILE_KB,
    NAME_PATTERN,
    SKILL_DIR_RESERVED_NAMES,
)

FRONTMATTER_RE = re.compile(r"\A---[ \t]*\r?\n(.*?\r?\n)---\r?\n", re.DOTALL)

# Patterns cần reject trong frontmatter (chống XML tag injection)
XML_TAG_RE = re.compile(r"<[a-zA-Z][^>]*>")


@dataclass
class Frontmatter:
    name: str | None = None
    description: str | None = None
    raw: str = ""

    @property
    def valid(self) -> bool:
        return bool(self.name and self.description)


@dataclass
class Manifest:
    format_version: str | None = None
    version: str | None = None
    title: str | None = None
    license: str | None = None
    maintainer: str | None = None
    permissions: dict = field(default_factory=dict)
    compatibility: dict = field(default_factory=dict)
    dependencies: dict = field(default_factory=dict)
    determinism: str | None = None
    tags: list[str] = field(default_factory=list)
    requires_skills: list[str] = field(default_factory=list)
    raw: dict = field(default_factory=dict)

    @property
    def declared_agents(self) -> list[str]:
        return list(self.compatibility.get("agents", []))


def _yaml_scalar(value: str) -> object:
    if not value:
        return None
    low = value.lower()
    if low in ("true", "yes"):
        return True
    if low in ("false", "no"):
        return False
    if low in ("null", "~"):
        return None
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_yaml_scalar(part.strip()) for part in inner.split(",")]
    return value


def _safe_load_yaml(text: str) -> tuple[dict | None, str | None]:
    """Parse YAML an toàn. Ưu tiên PyYAML SafeLoader, fallback parser thuần.

    Trả về (data, error). Parser thuần chỉ hỗ trợ tập con an toàn:
    mappings, sequences, scalars (str/int/float/bool/null), quoted strings.
    """
    try:
        import yaml  # type: ignore

        try:
            data = yaml.safe_load(text)
            return (data if isinstance(data, dict) else None), None
        except yaml.YAMLError as exc:
            return None, f"YAML parse error: {exc}"
    except ImportError:  # pragma: no cover - fallback path
        pass
    return _minimal_yaml_parse(text)


def _minimal_yaml_parse(text: str) -> tuple[dict | None, str | None]:
    """Fallback YAML parser thuần stdlib — tập con an toàn."""
    lines = text.splitlines()
    data: dict = {}
    stack: list[tuple[int, dict]] = [(-1, data)]
    try:
        for raw_line in lines:
            stripped = raw_line.rstrip()
            if not stripped or stripped.lstrip().startswith("#"):
                continue
            indent = len(raw_line) - len(raw_line.lstrip())
            if stripped.lstrip().startswith("- "):
                # sequence item: tìm list gần nhất trên stack
                value = _yaml_scalar(stripped.lstrip()[2:].strip())
                for _, cur in stack:
                    if isinstance(cur, dict):
                        for k, v in cur.items():
                            if isinstance(v, list):
                                v.append(value)
                                break
                continue
            if ":" not in stripped:
                continue
            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()
            parsed_value: object = _yaml_scalar(value) if value else None
            while len(stack) > 1 and indent <= stack[-1][0]:
                stack.pop()
            target = stack[-1][1]
            if value:
                target[key] = parsed_value
            else:
                # mapping hoặc sequence tiếp theo — tạo dict trước,
                # chuyển thành list khi gặp "- "
                target[key] = {}
                stack.append((indent, target[key]))
        return data, None
    except Exception as exc:  # noqa: BLE001
        return None, f"minimal yaml parse error: {exc}"


def parse_frontmatter(skill_md_path: Path) -> tuple[Frontmatter | None, str | None]:
    """Parse YAML frontmatter từ SKILL.md. Trả (frontmatter, error)."""
    try:
        raw = skill_md_path.read_bytes()
    except OSError as exc:
        return None, f"cannot read SKILL.md: {exc}"
    if len(raw) > MAX_SKILL_FILE_KB * 1024:
        return None, f"SKILL.md vượt giới hạn {MAX_SKILL_FILE_KB} KiB"
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return None, f"SKILL.md không phải UTF-8 hợp lệ: {exc}"

    match = FRONTMATTER_RE.match(text)
    if not match:
        return None, "SKILL.md thiếu YAML frontmatter (bắt đầu bằng ---)"

    fm_text = match.group(1)
    if len(fm_text.encode()) > MAX_FRONTMATTER_KB * 1024:
        return None, f"frontmatter vượt giới hạn {MAX_FRONTMATTER_KB} KiB"

    data, error = _safe_load_yaml(fm_text)
    if error or data is None:
        return None, f"frontmatter YAML không hợp lệ: {error or 'empty'}"

    name = data.get("name")
    description = data.get("description")
    if not isinstance(name, str) or not isinstance(description, str):
        return None, "frontmatter thiếu hoặc sai kiểu name/description (chuỗi bắt buộc)"
    if XML_TAG_RE.search(name) or XML_TAG_RE.search(description):
        return None, "frontmatter chứa XML tags (không được phép)"

    return Frontmatter(name=name, description=description, raw=fm_text), None


def parse_manifest(yaml_path: Path) -> tuple[Manifest | None, str | None]:
    """Parse skill.yaml. Trả (manifest, error)."""
    try:
        raw = yaml_path.read_bytes()
    except OSError as exc:
        return None, f"cannot read skill.yaml: {exc}"
    if len(raw) > MAX_MANIFEST_KB * 1024:
        return None, f"skill.yaml vượt giới hạn {MAX_MANIFEST_KB} KiB"
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return None, f"skill.yaml không phải UTF-8 hợp lệ: {exc}"

    data, error = _safe_load_yaml(text)
    if error or data is None:
        return None, f"skill.yaml không hợp lệ: {error or 'empty'}"

    def expect_str(key: str) -> str | None:
        v = data.get(key)
        return v if isinstance(v, str) else None

    manifest = Manifest(raw=data)
    manifest.format_version = expect_str("format_version")
    manifest.version = expect_str("version")
    manifest.title = expect_str("title")
    manifest.license = expect_str("license")
    manifest.maintainer = expect_str("maintainer")
    manifest.determinism = expect_str("determinism")

    perms = data.get("permissions")
    if isinstance(perms, dict):
        manifest.permissions = perms

    comp = data.get("compatibility")
    if isinstance(comp, dict):
        manifest.compatibility = comp

    deps = data.get("dependencies")
    if isinstance(deps, dict):
        manifest.dependencies = deps

    tags = data.get("tags")
    if isinstance(tags, list):
        manifest.tags = [t for t in tags if isinstance(t, str)]

    req = data.get("requires_skills")
    if isinstance(req, list):
        manifest.requires_skills = [r for r in req if isinstance(r, str)]

    return manifest, None


def validate_frontmatter(fm: Frontmatter, dir_name: str) -> list[str]:
    """Kiểm các rule name/description của frontmatter. Trả danh sách lỗi."""
    errors: list[str] = []
    assert fm.name  # caller phải đảm bảo
    if not NAME_PATTERN.match(fm.name):
        errors.append(
            "V-003: name phải khớp pattern [a-z0-9][a-z0-9-]{0,63}; "
            "chữ thường + số + gạch nối, không bắt đầu/kết thúc bằng dấu gạch nối"
        )
    reserved = (SKILL_DIR_RESERVED_NAMES & set(fm.name.split("-"))) | (
        SKILL_DIR_RESERVED_NAMES & {dir_name})
    if reserved:
        errors.append(f"V-003: name/dir chứa reserved word: {', '.join(sorted(reserved))}")
    if fm.name != dir_name:
        errors.append(f"V-010: tên thư mục '{dir_name}' != name frontmatter '{fm.name}'")
    if len(fm.description) < 30:
        errors.append(
            f"V-004: description quá ngắn ({len(fm.description)} chars, cần >= 30)"
        )
    return errors
