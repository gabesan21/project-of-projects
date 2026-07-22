#!/usr/bin/env python3
"""Installs or updates the standalone harness of an included repository.

Manifest v2 (`harness_root: "pop"`): files/directories/anatomy/keep_files are
relative to harness_root and go into `target/pop/`; the `.included-harness.json`
also lives in `pop/` (it is the marker that `poplib.vault_root` and
`pop_validate --standalone` use to detect the new anatomy). Skills,
AGENTS.md and CLAUDE.md always sit at the root of the target. Manifest v1 (no
`harness_root`) keeps the legacy layout at the root — zero regression.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parent.parent
MANIFEST = SOURCE / "_templates" / "included-manifest.json"
SKILLS_SOURCE = (SOURCE.parent / ".agents" / "skills"
                 if (SOURCE / ".included-harness.json").is_file()
                 else SOURCE / ".agents" / "skills")
EXTERNAL_LINK = re.compile(r"\[\[categories/[^/]+/[^/]+/([^\]|#]+)([^\]]*)\]\]")


def manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def localize(text: str, *, included_paths: bool = False) -> str:
    """Strips the parent-vault prefix from the wikilinks of an included project."""
    rendered = EXTERNAL_LINK.sub(
        lambda m: "[[" + m.group(1) + m.group(2) + "]]", text)
    if included_paths:
        rendered = re.sub(r"(?<!pop/)scripts/", "pop/scripts/", rendered)
    return rendered


def copy_file(source: Path, dest: Path, *, overwrite: bool = True,
              included_paths: bool = False) -> None:
    if dest.exists() and dest.is_dir():
        raise RuntimeError(f"collision with directory: {dest}")
    if dest.exists() and not overwrite:
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    if source.suffix in {".md", ".py", ".json"}:
        text = source.read_text(encoding="utf-8")
        dest.write_text(localize(text, included_paths=(included_paths and source.suffix == ".md")),
                        encoding="utf-8")
    else:
        shutil.copy2(source, dest)


def copy_tree(source: Path, dest: Path, *, included_paths: bool = False) -> None:
    for path in source.rglob("*"):
        if path.is_dir() or "__pycache__" in path.parts:
            continue
        copy_file(path, dest / path.relative_to(source),
                  included_paths=included_paths)


def preserve_worktree_marker(target: Path, prefix: str = "") -> None:
    """Allows versioning just the marker, even in repos that ignore worktrees/,
    and keeps the installed scripts' bytecode out of Git.
    `prefix` is the harness_root with a trailing slash (`pop/`) in the new anatomy."""
    ignore = target / ".gitignore"
    if not ignore.exists():
        return
    wt = f"{prefix}worktrees"
    block = (f"# included-harness: preserve the standalone anatomy in Git\n"
             f"!{wt}/\n{wt}/*\n!{wt}/.gitkeep\n")
    text = ignore.read_text(encoding="utf-8")
    if f"!{wt}/.gitkeep" not in text:
        text = text.rstrip() + "\n\n" + block
    if "__pycache__/" not in text:
        text = (text.rstrip() +
                "\n# included-harness: scripts' bytecode\n__pycache__/\n")
    ignore.write_text(text, encoding="utf-8")


def audit() -> list[str]:
    data = manifest()
    missing = []
    for name in data["files"]:
        if not (SOURCE / name).is_file(): missing.append(name)
    for name in data["directories"]:
        if not (SOURCE / name).is_dir(): missing.append(name)
    for name in data["skills"]:
        if not (SKILLS_SOURCE / name / "SKILL.md").is_file(): missing.append(f"skill:{name}")
    return missing


def install(target: Path) -> None:
    target = target.resolve()
    if not target.is_dir():
        raise RuntimeError(f"target is not a directory: {target}")
    missing = audit()
    if missing:
        raise RuntimeError("incomplete manifest: " + ", ".join(missing))
    data = manifest()
    # harness_root: "pop" in manifest v2; "" (target root) in legacy v1.
    hr = data.get("harness_root", "") or ""
    hb = target / hr if hr else target
    # Preflight: only explicitly managed paths may be written.
    for name in data["files"]:
        copy_file(SOURCE / name, hb / name, included_paths=True)
    for name in data["directories"]:
        copy_tree(SOURCE / name, hb / name, included_paths=True)
    for name in data["skills"]:
        copy_tree(SKILLS_SOURCE / name, target / ".agents/skills" / name,
                  included_paths=True)
    copy_file(MANIFEST, hb / ".included-harness.json")
    for rel in data["anatomy"]:
        (hb / rel).mkdir(parents=True, exist_ok=True)
    # Git does not preserve empty directories: these markers are a managed part
    # of the contract, so that a real clone keeps the whole standalone anatomy.
    for rel in data.get("keep_files", []):
        marker = hb / rel
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.touch()
    preserve_worktree_marker(target, f"{hr}/" if hr else "")
    # AGENTS belongs to the project: we never replace it. We only fix parent links.
    for path in target.rglob("*.md"):
        if ".git" in path.parts or "kanban" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        rendered = localize(text)
        if rendered != text:
            path.write_text(rendered, encoding="utf-8")
    agents = target / "AGENTS.md"
    if not agents.exists():
        copy_file(SOURCE / "_templates/AGENTS-PROJECT.md", agents)
    claude = target / "CLAUDE.md"
    if not claude.exists():
        claude.symlink_to("AGENTS.md")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs="?", type=Path)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--audit-manifest", action="store_true")
    args = parser.parse_args()
    missing = audit()
    if args.audit_manifest:
        if missing:
            print("incomplete manifest: " + ", ".join(missing), file=sys.stderr); return 1
        print("manifest complete"); return 0
    if not args.target:
        parser.error("target is required")
    if args.check:
        target_manifest = args.target / "pop" / ".included-harness.json"
        if not target_manifest.is_file():
            target_manifest = args.target / ".included-harness.json"
        if missing or not target_manifest.is_file():
            print("incomplete harness", file=sys.stderr); return 1
        print("harness installed"); return 0
    try:
        install(args.target)
    except RuntimeError as error:
        print(f"aborted: {error}", file=sys.stderr); return 1
    print(f"standalone harness installed at {args.target}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
