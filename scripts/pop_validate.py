#!/usr/bin/env python3
"""pop_validate — validates the PoP vault's limits and invariants.

Checks: root INDEX.md descriptions (<=144 chars) and category INDEX.md
descriptions (<=600 chars); harness notes with <=150 lines;
positive whitelist — only the harness folders, never the product code);
mandatory `pop/` anatomy in `categories/` projects (harness at the folder
root — `kanban/` or `.included-harness.json` outside `pop/` — is a
violation, the boundary of rule 13); required
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
import json
import hashlib
import re
import sys

import poplib

MAX_ROOT_DESC = 144
MAX_CAT_DESC = 600
MAX_NOTE_LINES = 150
EXEMPT_NAMES = {"AGENTS.md", "WORKFLOW.md", "README.md"}
CARD_REQUIRED = ("id", "project", "stage", "created", "updated")
SIZE_VALUES = {"S", "M", "L"}

ROOT_ENTRY = re.compile(r"^- \[\[.*?\]\]\s*—\s*(.+)$")
TASK_DIR = re.compile(r"^\d+\.\d+\.\d+-")
WIKILINK = re.compile(r"!?\[\[([^\]|#^]*)")
POP_HASH = re.compile(r"<!--\s*pop-hash:\s*(\S+)\s+sha256=([0-9a-fA-F]+)\s*-->")
INLINE_CODE = re.compile(r"`[^`]*`")
LINK_SKIP_PARTS = {"external-repository", ".obsidian", ".git", "worktrees",
                   "__pycache__", "node_modules", "vendor"}
# Suffixes of the task's own stage artifacts (created only as the task advances
# through the kanban): a card in 001-005 links `.plan/.approval/.verify` files
# not yet born — expected navigation link, not a real break (see [[WORKFLOW]]).
STAGE_ARTIFACT_SUFFIXES = (".plan", ".approval", ".verify")
EXTERNAL_PROJECT_LINK = re.compile(r"\[\[categories/[^/]+/[^/]+/")


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
    return MAX_NOTE_LINES


def check_note_sizes(root, projects, violations):
    """(c) harness .md files <=150 lines.

    Positive whitelist (`poplib.iter_harness_markdown`): the yardstick reaches
    only the harness folders of each discovered scope — never project files
    (code, repo docs, `project/`, vendor, `node_modules`). Each embedded repo
    of a `full-multi-repo` enters as its own scope, so its harness is covered
    but its code is not. The root (meta-project `pop`) is just one more scope,
    covered by its own planning folders.
    """
    for scope in projects:
        for path in poplib.iter_harness_markdown(scope):
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
            size = meta.get("size")
            if size not in (None, "") and str(size) not in SIZE_VALUES:
                violations.append(f"{card}:1: invalid `size` `{size}` "
                                  f"(use S | M | L)")


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
        harness = poplib.harness_root(project)
        wt_root = harness / "worktrees"
        if not wt_root.is_dir():
            continue
        for wt in sorted(p for p in wt_root.iterdir() if p.is_dir()):
            if not any(wt.iterdir()):
                continue
            if project == root and not TASK_DIR.match(wt.name):
                continue  # rule 19 session worktree, not a task worktree
            if not (harness / "kanban" / "004_processing" / wt.name).is_dir():
                warnings.append(f"{wt}: worktree without a matching task in "
                                f"004_processing")


# Unambiguous markers of a PoP harness outside `pop/`: a legacy project always
# has `kanban/` at the root (any type) or, if included, the manifest at the
# root. A `project/` folder without a harness is a not-yet-imported scaffold
# (not a PoP project) — it stays out, it is not an anatomy violation. Generic
# names (`scripts/`, `docs/`) that the product code may legitimately have also
# stay out, as the positive whitelist demands.
LEGACY_MARKERS = ("kanban", ".included-harness.json")


def _scan_legacy_markers(scope, root, violations):
    """Reports unambiguous harness markers outside `pop/` in a scope."""
    for name in LEGACY_MARKERS:
        if (scope / name).exists():
            violations.append(
                f"{(scope / name)}: harness outside `pop/` — legacy anatomy / "
                f"rule 13 boundary; move the harness into `pop/`")


def check_strict_anatomy(root, violations):
    """(i) mandatory `pop/` anatomy in `categories/` projects.

    In a project under `categories/` (and in each embedded repo of a
    full-multi-repo), no unambiguous PoP harness artifact may sit at the folder
    root: `kanban/` or `.included-harness.json` outside `pop/` is a violation —
    the whole harness lives in `pop/`. The vault root (meta-project) is exempt:
    its anatomy lives at the root by documented exception.
    """
    categories = root / "categories"
    if not categories.is_dir():
        return
    for project in sorted(categories.glob("*/*")):
        if not project.is_dir():
            continue
        if any(part.startswith(".") for part in project.relative_to(root).parts):
            continue
        _scan_legacy_markers(project, root, violations)
        # one level deeper: embedded repo of a full-multi-repo
        for sub in sorted(project.glob("*")):
            if sub.is_dir() and sub.name != "pop" and not sub.name.startswith("."):
                _scan_legacy_markers(sub, root, violations)


def check_wikilinks(root, warnings):
    """(f) broken wikilinks: target without a matching file (warning)."""
    targets = set()
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        # parts relative to the root: a folder name above the vault doesn't interfere
        if LINK_SKIP_PARTS & set(rel.parts):
            continue
        rel = rel.as_posix().lower()
        targets.update({path.name.lower(), path.stem.lower(), rel})
        if rel.endswith(".md"):
            targets.add(rel[:-3])
    # Origin restricted to the harness (whitelist): a broken wikilink in code or
    # vendor docs is noise, not signal. The collection of TARGETS above follows
    # the whole tree, so a harness link to a code file still resolves.
    for path in sorted(poplib.iter_all_harness_markdown(root)):
        if path.name.endswith(".excalidraw.md"):
            continue
        for n, line in lines_outside_fences(path):
            for m in WIKILINK.finditer(INLINE_CODE.sub("", line)):
                # trailing `\`: alias with an escaped pipe (`[[x\|y]]` in a table)
                target = m.group(1).strip().rstrip("\\")
                # skip empty (heading-only link), placeholder and ellipsis
                if not target or "<" in target or set(target) <= {"."}:
                    continue
                low = target.lower()
                name = low.rsplit("/", 1)[-1]
                if {low, f"{low}.md", name} & targets:
                    continue
                # Task link to a sibling stage artifact not yet created
                # (`<id>.plan|approval|verify`): expected navigation.
                src_stem = path.stem.lower()
                for suf in STAGE_ARTIFACT_SUFFIXES:
                    if src_stem.endswith(suf):
                        src_stem = src_stem[: -len(suf)]
                        break
                if name in {f"{src_stem}{suf}" for suf in STAGE_ARTIFACT_SUFFIXES}:
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


def check_standalone(root, violations):
    """Strict contract for an included clone, with no fallback to the parent vault.

    The harness lives in `pop/` (`hb`), with the `.included-harness.json` inside
    it; skills always sit at the repo root. Without `pop/` the check fails
    closed (manifest absent).
    """
    hb = root / "pop"
    manifest_path = hb / ".included-harness.json"
    if not manifest_path.is_file():
        violations.append(f"{manifest_path}: standalone manifest absent")
        return
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        violations.append(f"{manifest_path}: invalid JSON: {error}")
        return
    for name in data.get("files", []):
        if not (hb / name).is_file():
            violations.append(f"{hb / name}: required file absent")
    for name in data.get("directories", []):
        if not (hb / name).is_dir():
            violations.append(f"{hb / name}: required directory absent")
    for name in data.get("skills", []):
        path = root / ".agents/skills" / name / "SKILL.md"
        if not path.is_file():
            violations.append(f"{path}: required skill absent")
    for name in data.get("anatomy", []):
        if not (hb / name).is_dir():
            violations.append(f"{hb / name}: required anatomy absent")
    for name in data.get("keep_files", []):
        if not (hb / name).is_file():
            violations.append(f"{hb / name}: required Git marker absent")
    for path in root.rglob("*.md"):
        parts = set(path.relative_to(root).parts)
        if parts & {".git", "worktrees", "kanban"}:
            continue
        for n, line in lines_outside_fences(path):
            if EXTERNAL_PROJECT_LINK.search(line):
                violations.append(f"{path}:{n}: link points to the parent vault")


def main():
    parser = argparse.ArgumentParser(
        description="Validates vault limits: 144/600 chars, 150 lines, "
                    "card frontmatter, orphan worktrees, broken wikilinks "
                    "and pop-hash code-citation annotations.")
    parser.add_argument("--vault", metavar="DIR",
                        help="vault root (default: folder above scripts/)")
    parser.add_argument("--standalone", action="store_true",
                        help="fail closed for the local included contract")
    args = parser.parse_args()

    root = poplib.vault_root(args.vault)
    projects = poplib.discover_projects(root)
    categories = {poplib.project_label(root, p).split("/")[0]
                  for p in projects if p != root}

    violations, warnings = [], []
    check_root_index(root, violations)
    check_category_indexes(root, categories, violations)
    check_note_sizes(root, projects, violations)
    check_cards(root, projects, violations)
    check_release(root, projects, warnings)
    check_worktrees(root, projects, warnings)
    check_strict_anatomy(root, violations)
    check_wikilinks(root, warnings)
    check_hash_pins(root, violations)
    if args.standalone:
        check_standalone(root, violations)

    for w in warnings:
        print(f"[WARNING] {w}")
    for v in violations:
        print(f"[VIOLATION] {v}")
    if violations:
        print(f"\n{len(violations)} violation(s) found.")
        return 1
    if args.standalone:
        print("standalone valid")
    print("Vault valid — no violations found."
          + (f" ({len(warnings)} warning(s).)" if warnings else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
