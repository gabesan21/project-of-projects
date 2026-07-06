#!/usr/bin/env python3
"""pop_validate — validates the PoP vault's limits and invariants.

Checks: root INDEX.md descriptions (<=144 chars) and category INDEX.md
descriptions (<=600 chars); project notes with <=150 lines (plans <=200);
required frontmatter on task cards and `stage:` consistency with the
folder; orphan worktrees (warning); and broken wikilinks (warning — a
link to a future note is legitimate). Exit 1 if there is a violation;
warnings do not fail.

Usage:
    python3 scripts/pop_validate.py [--vault DIR]
"""

import argparse
import re
import sys

import poplib

MAX_ROOT_DESC = 144
MAX_CAT_DESC = 600
MAX_NOTE_LINES = 150
MAX_PLAN_LINES = 200
EXEMPT_NAMES = {"AGENTS.md", "WORKFLOW.md", "README.md"}
CARD_REQUIRED = ("id", "project", "stage", "created", "updated")

ROOT_ENTRY = re.compile(r"^- \[\[.*?\]\]\s*—\s*(.+)$")
WIKILINK = re.compile(r"!?\[\[([^\]|#^]*)")
INLINE_CODE = re.compile(r"`[^`]*`")
LINK_SKIP_PARTS = {"external-repository", ".obsidian", ".git", "worktrees",
                   "__pycache__", "node_modules"}


def lines_outside_fences(path):
    """Iterates (line number, line) skipping fenced code blocks."""
    in_fence = False
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield n, line


def check_root_index(root, violations):
    """(a) root INDEX.md: project description <=144 chars."""
    index = root / "INDEX.md"
    if not index.is_file():
        return
    for n, line in lines_outside_fences(index):
        m = ROOT_ENTRY.match(line.strip())
        if m and len(m.group(1)) > MAX_ROOT_DESC:
            violations.append(f"{index}:{n}: description with {len(m.group(1))} "
                              f"chars (max. {MAX_ROOT_DESC})")


def check_category_indexes(root, categories, violations):
    """(b) category INDEX.md: project description <=600 chars."""
    for category in sorted(categories):
        index = root / category / "INDEX.md"
        if not index.is_file():
            continue
        entry_start, desc = None, []

        def flush():
            if entry_start and len(" ".join(desc)) > MAX_CAT_DESC:
                violations.append(
                    f"{index}:{entry_start}: description with "
                    f"{len(' '.join(desc))} chars (max. {MAX_CAT_DESC})")

        for n, line in lines_outside_fences(index):
            stripped = line.strip()
            if stripped.startswith("#"):
                flush()
                entry_start = n if stripped.startswith("### ") else None
                desc = []
            elif entry_start and stripped and not stripped.startswith("- **Status:**"):
                desc.append(stripped)
        flush()


def note_limit(path):
    """Line limit for the file, or None if exempt."""
    if path.name in EXEMPT_NAMES:
        return None
    if path.name.endswith(".excalidraw.md"):
        return None  # Excalidraw diagram: embedded JSON, not a note
    if path.name.endswith(".plan.md"):
        return MAX_PLAN_LINES
    return MAX_NOTE_LINES


def check_note_sizes(root, projects, violations):
    """(c) project .md files and notes <=150 lines (plans <=200)."""
    scopes = list(projects)
    for extra in ("notes", "researches"):
        if (root / extra).is_dir():
            scopes.append(root / extra)
    for scope in scopes:
        for path in sorted(scope.rglob("*.md")):
            if "worktrees" in path.parts or "_templates" in path.parts:
                continue
            if "raw" in path.parts:
                continue  # raw research source: immutable, not a note
            limit = note_limit(path)
            if limit is None:
                continue
            count = len(path.read_text(encoding="utf-8").splitlines())
            if count > limit:
                violations.append(f"{path}:1: {count} lines (max. {limit})")


def check_cards(root, projects, violations):
    """(d) cards: required frontmatter and stage consistent with the folder."""
    for project in projects:
        for stage, task_dir, card in poplib.iter_cards(project):
            meta = poplib.read_card(card)
            for field in CARD_REQUIRED:
                if meta.get(field) in (None, ""):
                    violations.append(f"{card}:1: frontmatter missing `{field}`")
            if meta.get("stage") and meta["stage"] != stage:
                violations.append(f"{card}:1: stage `{meta['stage']}` differs "
                                  f"from folder `{stage}`")


def check_worktrees(root, projects, warnings):
    """(e) non-empty worktrees without a task in 004_processing (warning)."""
    for project in projects:
        wt_root = project / "worktrees"
        if not wt_root.is_dir():
            continue
        for wt in sorted(p for p in wt_root.iterdir() if p.is_dir()):
            if not any(wt.iterdir()):
                continue
            if not (project / "kanban" / "004_processing" / wt.name).is_dir():
                warnings.append(f"{wt}: worktree without a matching task in "
                                f"004_processing")


def check_wikilinks(root, warnings):
    """(f) broken wikilinks: target without a matching file (warning)."""
    targets = set()
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix().lower()
        if LINK_SKIP_PARTS & set(rel.split("/")):
            continue
        targets.update({path.name.lower(), path.stem.lower(), rel})
        if rel.endswith(".md"):
            targets.add(rel[:-3])
    for path in sorted(root.rglob("*.md")):
        parts = set(path.relative_to(root).parts)
        if parts & LINK_SKIP_PARTS or "_templates" in parts or "raw" in parts:
            continue
        if path.name.endswith(".excalidraw.md"):
            continue
        for n, line in lines_outside_fences(path):
            for m in WIKILINK.finditer(INLINE_CODE.sub("", line)):
                target = m.group(1).strip()
                # skip empty (heading-only link), placeholder and ellipsis
                if not target or "<" in target or set(target) <= {"."}:
                    continue
                low = target.lower()
                name = low.rsplit("/", 1)[-1]
                if {low, f"{low}.md", name} & targets:
                    continue
                warnings.append(f"{path}:{n}: broken wikilink [[{target}]]")


def main():
    parser = argparse.ArgumentParser(
        description="Validates vault limits: 144/600 chars, 150 lines, "
                    "card frontmatter, orphan worktrees and broken "
                    "wikilinks.")
    parser.add_argument("--vault", metavar="DIR",
                        help="vault root (default: folder above scripts/)")
    args = parser.parse_args()

    root = poplib.vault_root(args.vault)
    projects = poplib.discover_projects(root)
    categories = {poplib.project_label(root, p).split("/")[0] for p in projects}

    violations, warnings = [], []
    check_root_index(root, violations)
    check_category_indexes(root, categories, violations)
    check_note_sizes(root, projects, violations)
    check_cards(root, projects, violations)
    check_worktrees(root, projects, warnings)
    check_wikilinks(root, warnings)

    for w in warnings:
        print(f"[WARNING] {w}")
    for v in violations:
        print(f"[VIOLATION] {v}")
    if violations:
        print(f"\n{len(violations)} violation(s) found.")
        return 1
    print("Vault valid — no violations found."
          + (f" ({len(warnings)} warning(s).)" if warnings else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
