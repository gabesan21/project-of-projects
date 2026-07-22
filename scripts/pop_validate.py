#!/usr/bin/env python3

import argparse
import datetime
import hashlib
import json
import re
import sys

import poplib
import pop_roadmap

MAX_ROOT_DESC = 144
MAX_CAT_DESC = 600
MAX_NOTE_LINES = 150
EXEMPT_NAMES = {"AGENTS.md", "WORKFLOW.md", "README.md"}
CARD_REQUIRED = ("id", "project", "stage", "created", "updated")
ORIGIN_VALUES = ("roadmap", "modifications")
MODIFICATION_REF = re.compile(r"^M-\d+$")
SIZE_VALUES = {"S", "M", "L"}
SPEC_REQUIRED = (
    "id", "project", "domain", "kind", "status", "implementation",
    "origin", "created", "updated", "supersedes", "superseded_by",
)
SPEC_ENUMS = {
    "kind": {"contract", "overview"},
    "status": {"draft", "active", "superseded"},
    "implementation": {"planned", "partial", "implemented",
                       "not_applicable"},
}
KEBAB_CASE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

ROOT_ENTRY = re.compile(r"^- \[\[.*?\]\]\s*—\s*(.+)$")
TASK_DIR = re.compile(r"^(?:\d+\.\d+\.\d+|M-\d+\.\d+)-")
WIKILINK = re.compile(r"!?\[\[([^\]|#^]*)")
POP_HASH = re.compile(r"<!--\s*pop-hash:\s*(\S+)\s+sha256=([0-9a-fA-F]+)\s*-->")
INLINE_CODE = re.compile(r"`[^`]*`")
LINK_SKIP_PARTS = {"external-repository", ".obsidian", ".git", "worktrees",
                   "__pycache__", "node_modules", "vendor"}
# kanban): um card em 001-005 linka `.plan/.approval/.verify` que ainda no
STAGE_ARTIFACT_SUFFIXES = (".plan", ".approval", ".verify")
EXTERNAL_PROJECT_LINK = re.compile(r"\[\[categories/[^/]+/[^/]+/")


def _spec_links(path):
    links = []
    for _, line in lines_outside_fences(path):
        for match in WIKILINK.finditer(INLINE_CODE.sub("", line)):
            target = match.group(1).strip().rstrip("\\").split("#", 1)[0]
            if target:
                links.append(target)
    return links


def _spec_aliases(root, specs_dir, path):
    rel_collection = path.relative_to(specs_dir).with_suffix("").as_posix()
    rel_root = path.relative_to(root).with_suffix("").as_posix()
    return {path.stem, rel_collection, rel_root}


def _linked_specs(root, specs_dir, source, documents):
    aliases = {}
    for path in documents:
        for alias in _spec_aliases(root, specs_dir, path):
            aliases.setdefault(alias, set()).add(path)
    resolved = set()
    for target in _spec_links(source):
        matches = aliases.get(target.removesuffix(".md"), set())
        if len(matches) == 1:
            resolved.update(matches)
    return resolved


def _valid_iso_date(value):
    raw = str(value or "")
    try:
        parsed = datetime.date.fromisoformat(raw)
    except ValueError:
        return None
    return parsed if parsed.isoformat() == raw else None


def check_spec_collections(root, projects, violations):
    for project in projects:
        specs_dir = poplib.harness_root(project) / "specs"
        index = specs_dir / "INDEX.md"
        if not index.is_file():
            continue

        documents = sorted(path for path in specs_dir.rglob("*.md")
                           if path != index)
        metadata = {}
        ids = {}
        expected_project = poplib.project_label(root, project)

        for path in documents:
            rel = path.relative_to(specs_dir)
            if len(rel.parts) > 2:
                violations.append(
                    f"{path}:1: spec nesting is invalid; use at most "
                    "`specs/<domain>/file.md`")

            meta, _ = poplib.parse_frontmatter(
                path.read_text(encoding="utf-8"))
            metadata[path] = meta
            for field in SPEC_REQUIRED:
                if field not in meta:
                    violations.append(
                        f"{path}:1: frontmatter missing `{field}`")
                elif (field not in {"supersedes", "superseded_by"}
                      and meta[field] in (None, "")):
                    violations.append(
                        f"{path}:1: frontmatter has empty `{field}`")

            spec_id = meta.get("id")
            if not isinstance(spec_id, str) or not KEBAB_CASE.fullmatch(spec_id):
                violations.append(f"{path}:1: `id` invalid `{spec_id}` "
                                  "(use kebab-case)")
            elif spec_id in ids:
                violations.append(f"{path}:1: duplicate `id` `{spec_id}` "
                                  f"(also in {ids[spec_id]})")
            else:
                ids[spec_id] = path

            if meta.get("project") != expected_project:
                violations.append(
                    f"{path}:1: `project` `{meta.get('project')}` differs from "
                    f"scope label `{expected_project}`")

            domain = meta.get("domain")
            if not isinstance(domain, str) or not KEBAB_CASE.fullmatch(domain):
                violations.append(f"{path}:1: `domain` invalid `{domain}` "
                                  "(use kebab-case)")
            elif len(rel.parts) == 2 and domain != rel.parts[0]:
                violations.append(
                    f"{path}:1: `domain` `{domain}` differs from folder "
                    f"`{rel.parts[0]}`")

            for field, accepted in SPEC_ENUMS.items():
                if meta.get(field) not in accepted:
                    options = " | ".join(sorted(accepted))
                    violations.append(
                        f"{path}:1: `{field}` invalid `{meta.get(field)}` "
                        f"(use {options})")

            created = _valid_iso_date(meta.get("created"))
            updated = _valid_iso_date(meta.get("updated"))
            if created is None:
                violations.append(f"{path}:1: `created` invalid "
                                  f"`{meta.get('created')}` (use AAAA-MM-DD)")
            if updated is None:
                violations.append(f"{path}:1: `updated` invalid "
                                  f"`{meta.get('updated')}` (use AAAA-MM-DD)")
            if created and updated and updated < created:
                violations.append(f"{path}:1: `updated` precedes `created`")

            supersedes_value = meta.get("supersedes")
            if not isinstance(supersedes_value, list):
                violations.append(f"{path}:1: `supersedes` must be a list")
            else:
                for old_id in supersedes_value:
                    if (not isinstance(old_id, str)
                            or not KEBAB_CASE.fullmatch(old_id)):
                        violations.append(
                            f"{path}:1: invalid ID in `supersedes`: "
                            f"`{old_id}`")

            replacement_value = meta.get("superseded_by")
            if (replacement_value is not None
                    and (not isinstance(replacement_value, str)
                         or not KEBAB_CASE.fullmatch(replacement_value))):
                violations.append(
                    f"{path}:1: `superseded_by` invalid "
                    f"`{replacement_value}` (use a kebab-case ID)")

        for path, meta in metadata.items():
            spec_id = meta.get("id")
            status = meta.get("status")
            replacement_value = meta.get("superseded_by")
            replacement = (replacement_value
                           if isinstance(replacement_value, str) else None)
            supersedes = meta.get("supersedes")
            supersedes = supersedes if isinstance(supersedes, list) else []

            if status == "superseded" and not replacement:
                violations.append(
                    f"{path}:1: `superseded` spec missing `superseded_by`")
            if status in {"draft", "active"} and replacement:
                violations.append(
                    f"{path}:1: spec `{status}` cannot have `superseded_by`")
            if supersedes and status not in {"draft", "active"}:
                violations.append(
                    f"{path}:1: a spec that supersedes another must be draft or active")

            if replacement:
                replacement_path = ids.get(replacement)
                if replacement_path is None:
                    violations.append(
                        f"{path}:1: `superseded_by` references missing ID "
                        f"`{replacement}`")
                else:
                    replacement_meta = metadata[replacement_path]
                    if replacement_meta.get("status") not in {"draft", "active"}:
                        violations.append(
                            f"{path}:1: replacement `{replacement}` must be "
                            "draft or active")
                    if spec_id not in (replacement_meta.get("supersedes") or []):
                        violations.append(
                            f"{path}:1: non-reciprocal supersession with "
                            f"`{replacement}`")

            for old_id in supersedes:
                if not isinstance(old_id, str):
                    continue
                old_path = ids.get(old_id)
                if old_path is None:
                    violations.append(
                        f"{path}:1: `supersedes` references missing ID "
                        f"`{old_id}`")
                    continue
                old_meta = metadata[old_path]
                if old_meta.get("status") != "superseded":
                    violations.append(
                        f"{path}:1: superseded spec `{old_id}` must have status "
                        "superseded")
                if old_meta.get("superseded_by") != spec_id:
                    violations.append(
                        f"{path}:1: non-reciprocal supersession with `{old_id}`")

        direct = _linked_specs(root, specs_dir, index, documents)
        via_overview = set()
        for path in direct:
            if metadata[path].get("kind") == "overview":
                via_overview.update(
                    _linked_specs(root, specs_dir, path, documents))
        reachable = direct | via_overview
        for path, meta in metadata.items():
            if meta.get("status") in {"draft", "active"} and path not in reachable:
                violations.append(
                    f"{path}:1: spec `{meta.get('status')}` unreachable por "
                    "`specs/INDEX.md` diretamente ou via overview")


def lines_outside_fences(path):
    in_fence = False
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield n, line


def check_root_index(root, violations):
    index = root / "INDEX.md"
    if not index.is_file():
        return
    for n, line in lines_outside_fences(index):
        m = ROOT_ENTRY.match(line.strip())
        if m and len(m.group(1)) > MAX_ROOT_DESC:
            violations.append(f"{index}:{n}: description has {len(m.group(1))} "
                              f"characters (max. {MAX_ROOT_DESC})")


def check_category_indexes(root, categories, violations):
    for category in sorted(categories):
        index = root / "categories" / category / "INDEX.md"
        if not index.is_file():
            continue
        entry_start, desc = None, []

        def flush():
            if entry_start and len(" ".join(desc)) > MAX_CAT_DESC:
                violations.append(
                    f"{index}:{entry_start}: description has "
                    f"{len(' '.join(desc))} characters (max. {MAX_CAT_DESC})")

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
    if path.name in EXEMPT_NAMES:
        return None
    if path.name.endswith(".excalidraw.md"):
        return None  # Excalidraw diagram: embedded JSON, not a note.
    return MAX_NOTE_LINES


def check_note_sizes(root, projects, violations):
    for scope in projects:
        for path in poplib.iter_harness_markdown(scope):
            limit = note_limit(path)
            if limit is None:
                continue
            count = len(path.read_text(encoding="utf-8").splitlines())
            if count > limit:
                violations.append(f"{path}:1: {count} lines (max. {limit})")


def check_card_origin(card, meta, violations):
    """Origin frontmatter: roadmap requires epoch/phase; modifications
    requires `modification: M-<n>` (and does not require epoch/phase). An old
    card without `origin` is inferred from the id's `M-` prefix."""
    origin = meta.get("origin")
    if origin in (None, ""):
        origin = ("modifications"
                  if str(meta.get("id") or "").startswith("M-") else "roadmap")
    elif origin not in ORIGIN_VALUES:
        violations.append(f"{card}:1: `origin` invalid `{origin}` "
                          f"(use {' | '.join(ORIGIN_VALUES)})")
        return
    if origin == "roadmap":
        for field in ("epoch", "phase"):
            if meta.get(field) in (None, ""):
                violations.append(f"{card}:1: frontmatter missing `{field}` "
                                  "(roadmap origin)")
    elif not MODIFICATION_REF.fullmatch(str(meta.get("modification") or "")):
        violations.append(f"{card}:1: `modification` missing or invalid "
                          f"`{meta.get('modification')}` (use M-<n>)")


def check_cards(root, projects, violations):
    for project in projects:
        for stage, task_dir, card in poplib.iter_cards(project):
            meta = poplib.read_card(card)
            for field in CARD_REQUIRED:
                if meta.get(field) in (None, ""):
                    violations.append(f"{card}:1: frontmatter missing `{field}`")
            check_card_origin(card, meta, violations)
            if meta.get("stage") and meta["stage"] != stage:
                violations.append(f"{card}:1: stage `{meta['stage']}` differs "
                                  f"from folder `{stage}`")
            size = meta.get("size")
            if size not in (None, "") and str(size) not in SIZE_VALUES:
                violations.append(f"{card}:1: `size` invalid `{size}` "
                                  f"(use S | M | L)")
            for gate in ("003", "005"):
                key = f"yolo_{gate}_returns"
                if key not in meta:
                    continue
                try:
                    count = int(meta[key])
                except (TypeError, ValueError):
                    count = -1
                if count < 0 or count > poplib.YOLO_RETURN_LIMIT:
                    violations.append(
                        f"{card}:1: `{key}` invalid `{meta[key]}` (use 0..2)")
            if meta.get("circuit_breaker") is True and meta.get("blocked") is not True:
                violations.append(
                    f"{card}:1: circuit breaker requires `blocked: true`")
            telemetry = poplib.telemetry_path(task_dir)
            if telemetry.is_file():
                data = poplib.read_telemetry(task_dir)
                if not data["events"] and telemetry.stat().st_size:
                    violations.append(f"{telemetry}: telemetry invalid")


def check_release(root, projects, warnings):
    for project in projects:
        for stage, task_dir, card in poplib.iter_cards(project):
            if stage != "001_initial_task" and not poplib.task_released(card):
                warnings.append(f"{card}:1: in {stage} without `- [x] Ready "
                                f"to plan` — was the release gate skipped?")


def check_worktrees(root, projects, warnings):
    for project in projects:
        harness = poplib.harness_root(project)
        wt_root = harness / "worktrees"
        if not wt_root.is_dir():
            continue
        for wt in sorted(p for p in wt_root.iterdir() if p.is_dir()):
            if not any(wt.iterdir()):
                continue
            if project == root and not TASK_DIR.match(wt.name):
                continue  # Rule 19 session worktree, not a task worktree.
            if not (harness / "kanban" / "004_processing" / wt.name).is_dir():
                warnings.append(f"{wt}: worktree without a matching task in "
                                f"004_processing")


def check_roadmap_residuals(root, violations):
    """A completed task with memory cannot remain in the roadmap or the
    modifications (in MODIFICATIONS.md the leftover is the task wikilink)."""
    for scope, path, number, task_id in pop_roadmap.residuals(root):
        memory = pop_roadmap.memory_path(root, scope, task_id)
        # Ignore untracked external clones so validation never mutates their scope.
        if scope != root and not pop_roadmap.tracked(root, memory):
            continue
        violations.append(
            f"{path}:{number}: residual completed task `{task_id}` — "
            "remove the row (or the wikilink, in MODIFICATIONS.md) after "
            "validating memory")


# Legacy harness markers are rejected by the positive anatomy whitelist.
LEGACY_MARKERS = ("kanban", ".included-harness.json")


def _scan_legacy_markers(scope, root, violations):
    for name in LEGACY_MARKERS:
        if (scope / name).exists():
            violations.append(
                f"{(scope / name)}: harness outside `pop/` — legacy anatomy / "
                f"rule boundary 13; move the harness to `pop/`")


def check_strict_anatomy(root, violations):
    categories = root / "categories"
    if not categories.is_dir():
        return
    for project in sorted(categories.glob("*/*")):
        if not project.is_dir():
            continue
        if any(part.startswith(".") for part in project.relative_to(root).parts):
            continue
        _scan_legacy_markers(project, root, violations)
        for sub in sorted(project.glob("*")):
            if sub.is_dir() and sub.name != "pop" and not sub.name.startswith("."):
                _scan_legacy_markers(sub, root, violations)


def check_wikilinks(root, warnings):
    targets = set()
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if LINK_SKIP_PARTS & set(rel.parts):
            continue
        rel = rel.as_posix().lower()
        targets.update({path.name.lower(), path.stem.lower(), rel})
        if rel.endswith(".md"):
            targets.add(rel[:-3])
    for path in sorted(poplib.iter_all_harness_markdown(root)):
        if path.name.endswith(".excalidraw.md"):
            continue
        for n, line in lines_outside_fences(path):
            for m in WIKILINK.finditer(INLINE_CODE.sub("", line)):
                # A trailing backslash escapes a pipe in table aliases (`[[x\|y]]`).
                target = m.group(1).strip().rstrip("\\")
                if not target or "<" in target or set(target) <= {"."}:
                    continue
                low = target.lower()
                name = low.rsplit("/", 1)[-1]
                if {low, f"{low}.md", name} & targets:
                    continue
                src_stem = path.stem.lower()
                for suf in STAGE_ARTIFACT_SUFFIXES:
                    if src_stem.endswith(suf):
                        src_stem = src_stem[: -len(suf)]
                        break
                if name in {f"{src_stem}{suf}" for suf in STAGE_ARTIFACT_SUFFIXES}:
                    continue
                warnings.append(f"{path}:{n}: broken wikilink [[{target}]]")


def check_hash_pins(root, violations):
    for path in sorted(root.rglob("*.md")):
        parts = set(path.relative_to(root).parts)
        if parts & LINK_SKIP_PARTS or "_templates" in parts or "raw" in parts:
            continue
        for n, line in lines_outside_fences(path):
            for m in POP_HASH.finditer(line):
                relpath, digest = m.group(1), m.group(2).lower()
                if len(digest) != 64:
                    violations.append(f"{path}:{n}: malformed pop-hash "
                                      f"(sha256 has {len(digest)} hex digits, "
                                      f"expected 64)")
                    continue
                target = (path.parent / relpath).resolve()
                if not target.is_file():
                    violations.append(f"{path}:{n}: pop-hash cites missing file "
                                      f"`{relpath}`")
                    continue
                actual = hashlib.sha256(target.read_bytes()).hexdigest()
                if actual != digest:
                    violations.append(
                        f"{path}:{n}: pop-hash mismatch for `{relpath}` — "
                        f"the cited file changed; review the citation and "
                        f"update to sha256={actual}")


def check_standalone(root, violations):
    hb = root / "pop"
    manifest_path = hb / ".included-harness.json"
    if not manifest_path.is_file():
        violations.append(f"{manifest_path}: standalone manifest missing")
        return
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        violations.append(f"{manifest_path}: JSON invalid: {error}")
        return
    for name in data.get("files", []):
        if not (hb / name).is_file():
            violations.append(f"{hb / name}: required file missing")
    for name in data.get("directories", []):
        if not (hb / name).is_dir():
            violations.append(f"{hb / name}: required directory missing")
    for name in data.get("skills", []):
        path = root / ".agents/skills" / name / "SKILL.md"
        if not path.is_file():
            violations.append(f"{path}: required skill missing")
    for name in data.get("anatomy", []):
        if not (hb / name).is_dir():
            violations.append(f"{hb / name}: required anatomy directory missing")
    for name in data.get("keep_files", []):
        if not (hb / name).is_file():
            violations.append(f"{hb / name}: required Git marker missing")
    for path in root.rglob("*.md"):
        parts = set(path.relative_to(root).parts)
        if parts & {".git", "worktrees", "kanban"}:
            continue
        for n, line in lines_outside_fences(path):
            if EXTERNAL_PROJECT_LINK.search(line):
                violations.append(f"{path}:{n}: link points to parent vault")


def main():
    parser = argparse.ArgumentParser(
        description="Validate vault limits: 144/600 characters, 150 lines, "
                    "card frontmatter, orphaned worktrees, broken wikilinks, "
                    "adopted specs, and pop-hash code citations.")
    parser.add_argument("--vault", metavar="DIR",
                        help="vault root (default: directory above scripts/)")
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
    check_roadmap_residuals(root, violations)
    check_strict_anatomy(root, violations)
    check_spec_collections(root, projects, violations)
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
