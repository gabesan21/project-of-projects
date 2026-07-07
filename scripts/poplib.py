"""poplib — shared utilities for the PoP CLI scripts.

Provides: vault root detection, project discovery (`categories/<category>/<project>/`
folders with `kanban/`), a simple YAML frontmatter parser (key: value,
inline `[a, b]` lists and block `- item` lists) and task card helpers.
Stdlib only (Python >= 3.9).
"""

from __future__ import annotations

import datetime
import getpass
import re
import socket
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

# Default lease for the task claim (see pop_claim.py).
DEFAULT_LEASE_HOURS = 2

# Human release checkbox on the card (gate for leaving 001).
RELEASE_MARK = re.compile(r"^\s*[-*]\s*\[[xX]\]\s*Ready to plan")

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
    """Vault projects: `categories/<category>/<project>/` folders with `kanban/`."""
    projects = []
    for kanban in sorted(root.glob("categories/*/*/kanban")):
        if kanban.parent.parent.name.startswith("."):
            continue
        if kanban.is_dir():
            projects.append(kanban.parent)
    return projects


def project_label(root: Path, project: Path) -> str:
    """Short `<category>/<project>` name of a project folder."""
    return project.relative_to(root / "categories").as_posix()


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


def task_released(card: Path) -> bool:
    """True if the card has `- [x] Ready to plan` outside code fences."""
    in_fence = False
    for line in card.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence and RELEASE_MARK.match(line):
            return True
    return False


def default_agent() -> str:
    """Default agent identifier: user@host."""
    return f"{getpass.getuser()}@{socket.gethostname()}"


def now() -> datetime.datetime:
    return datetime.datetime.now().astimezone()


def parse_claim(meta: dict) -> Tuple[Optional[str], Optional[datetime.datetime]]:
    """Returns (claimed_by, claimed_at | None) from a card's frontmatter."""
    by = meta.get("claimed_by") or None
    raw = str(meta.get("claimed_at") or "")
    try:
        at = datetime.datetime.fromisoformat(raw)
        if at.tzinfo is None:
            at = at.astimezone()
    except ValueError:
        at = None
    return by, at


def claim_expired(at: Optional[datetime.datetime],
                  lease_hours: float = DEFAULT_LEASE_HOURS) -> bool:
    if at is None:
        return True  # a claim without a valid timestamp holds no lease
    return now() - at > datetime.timedelta(hours=lease_hours)


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
