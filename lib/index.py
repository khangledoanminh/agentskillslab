"""Skill search index: inverted index build từ filesystem.

Design:
- Build từ một hoặc nhiều skill root directories
- Index trên: name, title, tags, description (tokenized)
- Verified: 1.000 skills < 5s trên máy thường (xem benchmarks/)
- Không global state; mọi state nằm trong object Index
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .manifest import parse_frontmatter, parse_manifest

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has",
    "he", "in", "is", "it", "its", "of", "on", "or", "that", "the", "to",
    "was", "were", "will", "with", "use", "when", "this", "your", "you",
}

TOKEN_RE = re.compile(r"[a-z][a-z0-9-]*")


@dataclass
class SkillEntry:
    name: str
    title: str
    description: str
    tags: list[str]
    path: Path
    license: str
    determinism: str | None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "tags": self.tags,
            "path": str(self.path),
            "license": self.license,
            "determinism": self.determinism,
        }


class Index:
    def __init__(self) -> None:
        self.entries: list[SkillEntry] = []
        self._posting: dict[str, set[int]] = {}
        self._name_index: dict[str, int] = {}

    @property
    def size(self) -> int:
        return len(self.entries)

    def build(self, roots: list[Path], *, limit: int | None = None) -> list[str]:
        """Build index từ các skill root dirs. Trả danh sách warning."""
        warnings: list[str] = []
        seen_names: dict[str, Path] = {}
        for root in roots:
            if not root.is_dir():
                warnings.append(f"root '{root}' không tồn tại, bỏ qua")
                continue
            for skill_dir in sorted(root.iterdir()):
                if limit is not None and len(self.entries) >= limit:
                    return warnings
                if not skill_dir.is_dir() or skill_dir.name.startswith("."):
                    continue
                entry = self._load_entry(skill_dir)
                if entry is None:
                    continue
                idx = len(self.entries)
                self.entries.append(entry)
                if entry.name in seen_names:
                    warnings.append(
                        f"trùng tên skill '{entry.name}': {skill_dir} và {seen_names[entry.name]}"
                    )
                seen_names[entry.name] = skill_dir
                self._name_index[entry.name] = idx
                text = " ".join([
                    entry.name, entry.title, entry.description,
                    " ".join(entry.tags),
                ]).lower()
                for token in set(TOKEN_RE.findall(text)) - STOPWORDS:
                    self._posting.setdefault(token, set()).add(idx)
        return warnings

    def _load_entry(self, skill_dir: Path) -> SkillEntry | None:
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            return None
        fm, error = parse_frontmatter(skill_md)
        if fm is None or not fm.valid:
            return None

        manifest = None
        yaml_path = skill_dir / "skill.yaml"
        if yaml_path.exists():
            manifest, _ = parse_manifest(yaml_path)

        title = manifest.title if manifest and manifest.title else fm.name
        tags = manifest.tags if manifest else []
        license_ = manifest.license or "unknown"
        determinism = manifest.determinism if manifest else None

        return SkillEntry(
            name=fm.name,
            title=title,
            description=fm.description or "",
            tags=tags,
            path=skill_dir,
            license=license_,
            determinism=determinism,
        )

    def search(self, query: str, *, top: int = 10) -> list[tuple[float, SkillEntry]]:
        """Tìm kiếm theo query. Score = số token query khớp trong posting."""
        tokens = [t for t in TOKEN_RE.findall(query.lower()) if t not in STOPWORDS]
        if not tokens:
            return []
        scores: dict[int, int] = {}
        for token in tokens:
            for idx in self._posting.get(token, set()):
                scores[idx] = scores.get(idx, 0) + 1
        # exact name match boost
        for token in tokens:
            if token in self._name_index:
                idx = self._name_index[token]
                scores[idx] = scores.get(idx, 0) + 5

        ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
        return [(float(score) / len(tokens), self.entries[idx])
                for idx, score in ranked[:top]]

    def get(self, name: str) -> SkillEntry | None:
        idx = self._name_index.get(name)
        return self.entries[idx] if idx is not None else None
