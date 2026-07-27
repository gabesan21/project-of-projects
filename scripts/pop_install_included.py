#!/usr/bin/env python3
"""Installs and **updates** the standalone harness of a repository with an
embedded PoP.

The root PoP is the single source of the harness: no project evolves the
WORKFLOW, the templates or the scripts on its own — it receives a managed copy
of them. So that "update" is verifiable, every installation stamps the source's
`content_sha` of the managed set into `.included-harness.json`;
`--check-fresh` recomputes it and fails closed when the target has fallen
behind. Without the stamp there is no way to tell a current clone from a clone
stuck on an old version of the flow.

Manifest v2 (`harness_root: "pop"`): files/directories/anatomy/keep_files are
relative to harness_root and go into `target/pop/`; the `.included-harness.json`
also lives in `pop/` (it is the marker that `poplib.vault_root` and
`pop_validate --standalone` use to detect the new anatomy). Skills,
AGENTS.md and CLAUDE.md always sit at the root of the target. Manifest v1 (no
`harness_root`) keeps the legacy layout at the root — zero regression.
"""
from __future__ import annotations

import argparse
import hashlib
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
# Manifest fallback: the target gets the harness, not the parent's tooling.
DEFAULT_EXCLUDE = ("__pycache__", "tests", ".pytest_cache")


def manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def excluded(data, relative: Path) -> bool:
    """A path the installer does not propagate (bytecode, the parent's suite)."""
    names = set(data.get("exclude", DEFAULT_EXCLUDE))
    return bool(names.intersection(relative.parts))


def managed_sources(data):
    """`(stable label, file)` for everything the installer propagates.

    The label is independent of the target's layout, so the `content_sha` only
    changes when the harness's **content** changes — not when the destination
    changes.
    """
    for name in data["files"]:
        yield name, SOURCE / name
    for name in data["directories"]:
        base = SOURCE / name
        for path in sorted(base.rglob("*")):
            relative = path.relative_to(base)
            if path.is_file() and not excluded(data, relative):
                yield f"{name}/{relative.as_posix()}", path
    for name in data["skills"]:
        base = SKILLS_SOURCE / name
        for path in sorted(base.rglob("*")):
            relative = path.relative_to(base)
            if path.is_file() and not excluded(data, relative):
                yield f"skills/{name}/{relative.as_posix()}", path
    yield "manifest", MANIFEST


def content_sha(data=None) -> str:
    """Fingerprint of the harness at the source — the real version number."""
    data = data or manifest()
    digest = hashlib.sha256()
    for label, path in sorted(managed_sources(data)):
        digest.update(label.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def installed_stamp(target: Path):
    """`(marker path, recorded content_sha)` of the target; sha `None` if absent."""
    marker = target / "pop" / ".included-harness.json"
    if not marker.is_file():
        marker = target / ".included-harness.json"
    if not marker.is_file():
        return None, None
    try:
        return marker, json.loads(marker.read_text(encoding="utf-8")).get("content_sha")
    except json.JSONDecodeError:
        return marker, None


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


def copy_tree(source: Path, dest: Path, *, included_paths: bool = False,
              data=None) -> None:
    """Mirrors `source` into `dest`: copies what exists and **removes what left**.

    Without the pruning, a file deleted at the source survives forever in the
    target — the clone would keep offering a template or a script the flow has
    already retired.
    """
    data = data or manifest()
    kept = set()
    for path in source.rglob("*"):
        relative = path.relative_to(source)
        if path.is_dir() or excluded(data, relative):
            continue
        kept.add(relative)
        copy_file(path, dest / relative, included_paths=included_paths)
    if not dest.is_dir():
        return
    for path in sorted(dest.rglob("*"), reverse=True):
        relative = path.relative_to(dest)
        if path.is_file() and relative not in kept:
            path.unlink()
        elif path.is_dir() and not any(path.iterdir()):
            path.rmdir()


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
        copy_tree(SOURCE / name, hb / name, included_paths=True, data=data)
    for name in data["skills"]:
        copy_tree(SKILLS_SOURCE / name, target / ".agents/skills" / name,
                  included_paths=True, data=data)
    # The marker is the manifest plus this installation's content stamp.
    stamp = dict(data, content_sha=content_sha(data))
    (hb / ".included-harness.json").write_text(
        json.dumps(stamp, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
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
    parser.add_argument("--check", action="store_true",
                        help="is the harness installed in the target?")
    parser.add_argument("--check-fresh", action="store_true",
                        help="is the target's harness at the source's version?")
    parser.add_argument("--audit-manifest", action="store_true")
    parser.add_argument("--sha", action="store_true",
                        help="print the content_sha of the harness at the source")
    args = parser.parse_args()
    missing = audit()
    if args.audit_manifest:
        if missing:
            print("incomplete manifest: " + ", ".join(missing), file=sys.stderr); return 1
        print("manifest complete"); return 0
    if args.sha:
        print(content_sha()); return 0
    if not args.target:
        parser.error("target is required")
    if args.check:
        marker, _ = installed_stamp(args.target)
        if missing or marker is None:
            print("incomplete harness", file=sys.stderr); return 1
        print("harness installed"); return 0
    if args.check_fresh:
        if missing:
            print("incomplete manifest: " + ", ".join(missing), file=sys.stderr)
            return 1
        marker, stamped = installed_stamp(args.target)
        if marker is None:
            print(f"harness absent in {args.target}", file=sys.stderr); return 1
        current = content_sha()
        if stamped is None:
            print(f"harness without a stamp in {marker} — installed before "
                  f"content_sha; reinstall to date it", file=sys.stderr)
            return 1
        if stamped != current:
            print(f"harness STALE in {args.target}: target {stamped[:12]} "
                  f"≠ source {current[:12]} — run "
                  f"`pop_install_included.py {args.target}`", file=sys.stderr)
            return 1
        print(f"harness current ({current[:12]})"); return 0
    try:
        install(args.target)
    except RuntimeError as error:
        print(f"aborted: {error}", file=sys.stderr); return 1
    print(f"standalone harness installed at {args.target}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
