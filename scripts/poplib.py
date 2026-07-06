"""poplib — shared utilities for the PoP CLI scripts.

Provides: vault root detection, project discovery (`<category>/<project>/`
folders with `kanban/`), a simple YAML frontmatter parser (key: value,
inline `[a, b]` lists and block `- item` lists) and task card helpers.
Stdlib only (Python >= 3.9).
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Iterator, Optional, Tuple

STAGES = [
    "001_initial_task",
    "002_planning",
    "003_human_approval",
    "004_processing",
    "005_verifying",
    "006_done",
]

# Top-level folders that are never a project category.
IGNORED_TOP = {
    "external-repository",
    "_templates",
    ".obsidian",
    "researches",
    "notes",
    "scripts",
    "worktrees",
    ".git",
}


def vault_root(override: Optional[str] = None) -> Path:
    """Vault root: `--vault` if given, otherwise the folder above `scripts/`."""
    if override:
        return Path(override).resolve()
    return Path(__file__).resolve().parent.parent


def today() -> str:
    """Today's date in YYYY-MM-DD."""
    return datetime.date.today().isoformat()


def _coerce(raw: str):
    """Converts a frontmatter scalar: quotes, booleans, empty."""
    raw = raw.strip()
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ("'", '"'):
        return raw[1:-1]
    if raw.lower() == "true":
        return True
    if raw.lower() == "false":
        return False
    if raw == "":
        return None
    return raw


def _parse_value(raw: str):
    """Value of a key: scalar or inline list `[a, b]`."""
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        return [_coerce(item) for item in inner.split(",")]
    return _coerce(raw)


def parse_frontmatter(text: str) -> Tuple[dict, str]:
    """Splits frontmatter and body. No frontmatter -> ({}, text).

    Supports `key: value`, inline lists `[a, b]` and block lists
    (`key:` followed by `- item` lines).
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    meta: dict = {}
    current = None
    end = None
    for i in range(1, len(lines)):
        line = lines[i]
        if line.strip() == "---":
            end = i
            break
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- ") and current is not None:
            if not isinstance(meta[current], list):
                meta[current] = []
            meta[current].append(_coerce(stripped[2:]))
            continue
        if ":" in stripped and not line.startswith((" ", "\t")):
            key, _, raw = line.partition(":")
            current = key.strip()
            meta[current] = _parse_value(raw)
    if end is None:  # frontmatter without closing delimiter
        return {}, text
    return meta, "\n".join(lines[end + 1:])


def discover_projects(root: Path) -> list:
    """Vault projects: `<category>/<project>/` folders with `kanban/`."""
    projects = []
    for kanban in sorted(root.glob("*/*/kanban")):
        category = kanban.parent.parent.name
        if category in IGNORED_TOP or category.startswith("."):
            continue
        if kanban.is_dir():
            projects.append(kanban.parent)
    return projects


def project_label(root: Path, project: Path) -> str:
    """Short `<category>/<project>` name of a project folder."""
    return project.relative_to(root).as_posix()


def iter_cards(project: Path) -> Iterator[Tuple[str, Path, Path]]:
    """Iterates (stage, task_folder, card.md) of a project."""
    for stage in STAGES:
        stage_dir = project / "kanban" / stage
        if not stage_dir.is_dir():
            continue
        for task_dir in sorted(p for p in stage_dir.iterdir() if p.is_dir()):
            card = task_dir / f"{task_dir.name}.md"
            if card.is_file():
                yield stage, task_dir, card


def read_card(card: Path) -> dict:
    """Frontmatter of a card, as a dict (empty if absent)."""
    meta, _ = parse_frontmatter(card.read_text(encoding="utf-8"))
    return meta


def find_task(root: Path, task_id: str):
    """Locates the task by folder name in any project/stage.

    Returns (project, stage, task_folder) or None.
    """
    for project in discover_projects(root):
        for stage in STAGES:
            task_dir = project / "kanban" / stage / task_id
            if task_dir.is_dir():
                return project, stage, task_dir
    return None
