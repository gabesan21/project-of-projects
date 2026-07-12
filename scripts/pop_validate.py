#!/usr/bin/env python3
"""pop_validate — validates the PoP vault's limits and invariants.

Checks: root INDEX.md descriptions (<=144 chars) and category INDEX.md
descriptions (<=600 chars); project notes with <=150 lines (plans <=200;
`project/` — execution and clones — is outside the yardstick); required
frontmatter on task cards and `stage:` consistency with the
folder; orphan worktrees (warning); broken wikilinks (warning — a
link to a future note is legitimate); and `<!-- pop-hash: <path>
sha256=<hash> -->` code-citation annotations (fail-closed: a nonexistent
cited file or a divergent hash is a violation — see DOX rule 9). Exit 1
if there is a violation; warnings do not fail.

Usage:
    python3 scripts/pop_validate.py [--vault DIR]
"""

import argparse
import hashlib
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
POP_HASH = re.compile(r"<!--\s*pop-hash:\s*(\S+)\s+sha256=([0-9a-fA-F]+)\s*-->")
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
        index = root / "categories" / category / "INDEX.md"
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
    for extra in ("notes", "researches", "open_questions", "drafts"):
        if (root / extra).is_dir():
            scopes.append(root / extra)
    for scope in scopes:
        for path in sorted(scope.rglob("*.md")):
            if "worktrees" in path.parts or "_templates" in path.parts:
                continue
            if "raw" in path.parts:
                continue  # raw research source: immutable, not a note
            if "project" in path.relative_to(scope).parts:
                continue  # execution/clones: not notes; an embedded repo
                          # (full-multi-repo) is swept as its own scope
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


def check_release(root, projects, warnings):
    """(g) card beyond 001 without the release checked (warning)."""
    for project in projects:
        for stage, task_dir, card in poplib.iter_cards(project):
            if stage != "001_initial_task" and not poplib.task_released(card):
                warnings.append(f"{card}:1: in {stage} without `- [x] Ready "
                                f"to plan` — release gate skipped?")


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


def check_hash_pins(root, violations):
    """(h) pop-hash annotations: the cited file exists and the hash matches.

    Fail-closed (DOX rule 9): a malformed annotation, a nonexistent cited
    file or a divergent hash is a violation. The path is relative to the
    folder of the file carrying the annotation; the divergence message
    prints the current hash to paste after revising the citation.
    """
    for path in sorted(root.rglob("*.md")):
        parts = set(path.relative_to(root).parts)
        if parts & LINK_SKIP_PARTS or "_templates" in parts or "raw" in parts:
            continue
        for n, line in lines_outside_fences(path):
            for m in POP_HASH.finditer(line):
                relpath, digest = m.group(1), m.group(2).lower()
                if len(digest) != 64:
                    violations.append(f"{path}:{n}: malformed pop-hash "
                                      f"(sha256 with {len(digest)} hex "
                                      f"chars, expected 64)")
                    continue
                target = (path.parent / relpath).resolve()
                if not target.is_file():
                    violations.append(f"{path}:{n}: pop-hash cites a "
                                      f"nonexistent file `{relpath}`")
                    continue
                actual = hashlib.sha256(target.read_bytes()).hexdigest()
                if actual != digest:
                    violations.append(
                        f"{path}:{n}: divergent pop-hash for `{relpath}` "
                        f"— the cited file changed; revise the citation "
                        f"and update to sha256={actual}")


def main():
    parser = argparse.ArgumentParser(
        description="Validates vault limits: 144/600 chars, 150 lines, "
                    "card frontmatter, orphan worktrees, broken wikilinks "
                    "and pop-hash code-citation annotations.")
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
    check_release(root, projects, warnings)
    check_worktrees(root, projects, warnings)
    check_wikilinks(root, warnings)
    check_hash_pins(root, violations)

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
