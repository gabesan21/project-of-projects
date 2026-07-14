"""poplib — shared utilities for the PoP CLI scripts.

Provides: vault root detection, project discovery, a simple YAML frontmatter
parser (key: value, inline `[a, b]` lists and block `- item` lists) and task
card helpers. Single anatomy: the harness lives in `pop/`
(`categories/<c>/<p>/pop/kanban`, embedded repo in `<c>/<p>/<repo>/pop/kanban`);
the vault root (meta-project) keeps its kanban at the root as a documented
exception. `harness_root()` decides by scope. The legacy anatomy (harness at
the folder root) is no longer supported. Stdlib only (Python >= 3.9).
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
    """Vault root: `--vault` if given, otherwise the folder above `scripts/`.

    In an included clone the scripts live in `pop/scripts/`: if the folder
    above is named `pop` and holds `.included-harness.json`, the root is the
    folder above it (the repo root).
    """
    if override:
        return Path(override).resolve()
    base = Path(__file__).resolve().parent.parent
    if base.name == "pop" and (base / ".included-harness.json").is_file():
        return base.parent
    return base


def harness_root(project: Path) -> Path:
    """Harness root of a scope: `pop/` in `categories/` projects; the scope
    itself only at the vault root (meta-project, kanban at the root)."""
    return project / "pop" if (project / "pop" / "kanban").is_dir() else project


def templates_dir(root: Path) -> Path:
    """Vault templates folder: `pop/_templates` if it exists, else `_templates`."""
    new = root / "pop" / "_templates"
    return new if new.is_dir() else root / "_templates"


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
    """Vault project scopes, all in the `pop/` anatomy: the root (meta-project
    `pop` — kanban at the root, by documented exception — or an included clone,
    with `pop/kanban`), projects in `categories/<c>/<p>/pop/kanban` and the
    embedded repos of `full-multi-repo` projects in
    `categories/<c>/<p>/<repo>/pop/kanban`. The legacy anatomy (harness at the
    root) is no longer recognized — the validator reports it as a violation
    (see `check_strict_anatomy`)."""
    scopes = set()
    if (root / "kanban").is_dir() or (root / "pop" / "kanban").is_dir():
        scopes.add(root)
    # (pattern, number of kanban levels up to the scope)
    patterns = (
        ("categories/*/*/pop/kanban", 2),      # project
        ("categories/*/*/*/pop/kanban", 2),    # embedded repo (full-multi-repo)
    )
    for pattern, up in patterns:
        for kanban in root.glob(pattern):
            if not kanban.is_dir():
                continue
            scope = kanban.parents[up - 1]
            rel = scope.relative_to(root)
            if any(part.startswith(".") for part in rel.parts):
                continue
            scopes.add(scope)
    return sorted(scopes)


# PoP harness folders inside a project scope: these are the ONLY ones the
# size/wikilink checks reach. Positive whitelist — whatever belongs to the
# project (code, repo docs, clones, `project/`, embedded repo, vendor) stays
# out by construction, without depending on the type. The names are invariant
# across types (see TYPES.md): only the location of the code changes, and
# `discover_projects` already hands over the right scope, including each
# embedded repo of a full-multi-repo.
HARNESS_DIRS = ("roadmap", "specs", "researches", "skills", "notes",
                "memory", "open_questions", "drafts", "kanban")
HARNESS_ROOT_FILES = ("PROJECT.md", "ROADMAP.md")  # INDEX.md has its own budget (144/600)
# Belt and suspenders: never descend into raw research sources or into code that
# might be nested under a harness folder.
_HARNESS_SKIP = {"raw", "worktrees", "_templates", "__pycache__",
                 "node_modules", "vendor", ".git", ".obsidian"}


def iter_harness_markdown(scope: Path) -> Iterator[Path]:
    """Harness `.md` under a project scope (positive whitelist).

    In the current anatomy the whole harness (including PROJECT.md/ROADMAP.md)
    lives in `pop/` — `harness_root()` resolves it; the HARNESS_DIRS names
    don't change.
    """
    hroot = harness_root(scope)
    for name in HARNESS_ROOT_FILES:
        if (hroot / name).is_file():
            yield hroot / name
    for name in HARNESS_DIRS:
        base = hroot / name
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.md")):
            if not (_HARNESS_SKIP & set(path.relative_to(hroot).parts)):
                yield path


def iter_all_harness_markdown(root: Path) -> Iterator[Path]:
    """Harness `.md` of every discovered scope, without repetition."""
    seen = set()
    for scope in discover_projects(root):
        for path in iter_harness_markdown(scope):
            if path not in seen:
                seen.add(path)
                yield path


def project_label(root: Path, project: Path) -> str:
    """Short `<category>/<project>` name of a project folder — or
    `<category>/<project>/<repo>` for an embedded repo of a full-multi-repo.
    The vault root (meta-project) has the fixed label `pop`."""
    if project == root:
        return "pop"
    parts = project.relative_to(root / "categories").parts
    return "/".join(parts)


def project_dir(root: Path, label: str) -> Path:
    """Inverse of `project_label`: project folder from the label.

    `<cat>/<proj>` -> `categories/<cat>/<proj>`;
    `<cat>/<proj>/<repo>` -> `categories/<cat>/<proj>/<repo>` (embedded repo
    of a full-multi-repo, `pop/` anatomy);
    `pop` -> vault root (meta-project).
    """
    if label == "pop":
        return root
    parts = [p for p in label.split("/") if p]
    return root.joinpath("categories", *parts)


def iter_cards(project: Path) -> Iterator[Tuple[str, Path, Path]]:
    """Iterates (stage, task_folder, card.md) of a project."""
    for stage in STAGES:
        stage_dir = harness_root(project) / "kanban" / stage
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
        kanban = harness_root(project) / "kanban"
        for stage in STAGES:
            task_dir = kanban / stage / task_id
            if task_dir.is_dir():
                return project, stage, task_dir
    return None
