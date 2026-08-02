#!/usr/bin/env python3
"""Create explicitly confirmed local sandboxes for coding agents."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import poplib


AGENTS = ("claude-code", "codex", "opencode", "pi", "kimi-code")
COMMON_BINDS = (
    (".git-credentials", "file"),
    (".gitconfig", "file"),
    (".config/git", "directory"),
    (".config/gh", "directory"),
)
AGENT_BINDS = {
    "claude-code": (".claude", "directory"),
    "codex": (".codex", "directory"),
    "opencode": (".config/opencode", "directory"),
    "pi": (".pi", "directory"),
    "kimi-code": (".kimi-code", "directory"),
}
REQUIRED_TEMPLATES = (
    "Dockerfile", "entrypoint.sh", "start.sh", "stop.sh", "clean.sh",
    "sandbox.json", "profile.schema.json", "catalog.json", "seccomp-docker.json",
)
PACKAGE = re.compile(r"^[a-z0-9][a-z0-9+.-]*$")
STACK_MANIFESTS = frozenset({
    "Cargo.toml", "Dockerfile", "Pipfile", "composer.json", "compose.yaml",
    "compose.yml", "docker-compose.yaml", "docker-compose.yml", "go.mod",
    "package.json", "pnpm-lock.yaml", "pyproject.toml", "requirements.txt",
    "yarn.lock",
})
STACK_EXCLUDED_DIRS = frozenset({
    ".cache", ".git", ".mypy_cache", ".next", ".nox", ".opencode",
    ".pytest_cache", ".ruff_cache", ".tox", ".venv", "__pycache__",
    "build", "coverage", "dist", "node_modules", "pop", "target", "vendor",
    "venv",
})


class SandboxError(RuntimeError):
    """Contract error shown to the user without a traceback."""


def canonical(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def resolve_project(root: Path, value: str) -> tuple[str, Path]:
    """Resolve only labels returned by the poplib discovery API."""
    if Path(value).is_absolute() or ".." in Path(value).parts:
        raise SandboxError("project must be a scope label, without an external path or traversal")
    projects = {
        poplib.project_label(root, project): project
        for project in poplib.discover_projects(root)
    }
    if value not in projects:
        raise SandboxError(f"unknown project: {value}")
    project = projects[value]
    resolved = project.resolve(strict=True)
    if not _inside(resolved, root.resolve(strict=True)):
        raise SandboxError(f"project escapes the scope root: {value}")
    return value, resolved


def validate_agent(agent: str) -> None:
    if agent not in AGENTS:
        raise SandboxError(f"unknown agent: {agent}")


def template_root(root: Path) -> Path:
    path = poplib.templates_dir(root) / "coding-dockers"
    if not path.is_dir():
        raise SandboxError(f"missing templates: {path}")
    return path


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SandboxError(f"invalid JSON at {path}: {exc}") from exc


def load_templates(root: Path) -> tuple[Path, dict[str, Any], dict[str, Any], str]:
    base = template_root(root)
    missing = [name for name in REQUIRED_TEMPLATES if not (base / name).is_file()]
    if missing:
        raise SandboxError("missing required templates: " + ", ".join(missing))
    schema = read_json(base / "profile.schema.json")
    catalog = read_json(base / "catalog.json")
    if not isinstance(schema, dict) or not isinstance(catalog, dict):
        raise SandboxError("schema and catalog must be JSON objects")
    recipes = base / "recipes"
    found = {path.stem for path in recipes.glob("*.json")} if recipes.is_dir() else set()
    if found != set(AGENTS):
        raise SandboxError("incompatible recipe catalog; expected exactly: " + ", ".join(AGENTS))
    entries = catalog.get("agents")
    declared = {
        item.get("slug"): item.get("recipe") for item in entries
        if isinstance(item, dict)
    } if isinstance(entries, list) else {}
    expected = {agent: f"recipes/{agent}.json" for agent in AGENTS}
    if declared != expected:
        raise SandboxError("catalog.json does not declare exactly the five expected slots")
    content = []
    for path in sorted(item for item in base.rglob("*") if item.is_file()):
        content.append((path.relative_to(base).as_posix(), hashlib.sha256(path.read_bytes()).hexdigest()))
    return base, schema, catalog, digest(content)


def _binds(catalog: dict[str, Any], recipe: dict[str, Any], agent: str) -> list[dict[str, Any]]:
    home = Path.home().resolve()
    common = catalog.get("common_binds")
    state = recipe.get("state")
    if not isinstance(common, list) or not isinstance(state, dict):
        raise SandboxError("catalog/recipe does not declare required binds")
    entries = [*common, {
        "host_path": state.get("host_path"),
        "container_path": state.get("container_path"),
        "kind": state.get("kind"),
    }]
    result = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise SandboxError("invalid declarative bind")
        host_path = entry.get("host_path")
        target = entry.get("container_path")
        kind = entry.get("kind")
        if (not isinstance(host_path, str) or not host_path.startswith("~/")
                or not isinstance(target, str) or not target.startswith("/home/coder/")
                or kind not in {"file", "directory"}):
            raise SandboxError("declarative bind escapes the contract")
        source = home / host_path[2:]
        result.append({"source": str(source), "target": target,
                       "kind": kind, "read_only": False})
    specs = (*COMMON_BINDS, AGENT_BINDS[agent])
    expected = {
        (str(home / relative), str(Path("/home/coder") / relative), kind)
        for relative, kind in specs
    }
    actual = {(item["source"], item["target"], item["kind"]) for item in result}
    if len(result) != len(specs) or actual != expected:
        raise SandboxError("catalog/recipe does not declare exactly the contract binds")
    return result


def _stack_manifests(project: Path) -> list[Path]:
    """List only first-party manifests below the project in stable order."""
    manifests = []
    for directory, names, files in os.walk(project, topdown=True, followlinks=False):
        names[:] = sorted(name for name in names if name not in STACK_EXCLUDED_DIRS)
        base = Path(directory)
        manifests.extend(
            base / name for name in sorted(files)
            if name in STACK_MANIFESTS and not (base / name).is_symlink()
        )
    return manifests


def _composer_requires_sail(manifest: Path) -> bool:
    data = read_json(manifest)
    if not isinstance(data, dict):
        raise SandboxError(f"composer.json must be a JSON object: {manifest}")
    packages = []
    for field in ("require", "require-dev"):
        dependencies = data.get(field, {})
        if not isinstance(dependencies, dict):
            raise SandboxError(f"invalid {field} field in {manifest}")
        packages.extend(dependencies)
    return "laravel/sail" in packages


def detect_stack(project: Path) -> dict[str, Any]:
    manifests = _stack_manifests(project)
    names = {manifest.name for manifest in manifests}
    composer_manifests = [manifest for manifest in manifests if manifest.name == "composer.json"]
    docker_names = {
        "Dockerfile", "compose.yaml", "compose.yml", "docker-compose.yaml",
        "docker-compose.yml",
    }
    node = bool(names & {"package.json", "pnpm-lock.yaml", "yarn.lock"})
    php = bool(composer_manifests)
    return {
        "node": node,
        "yarn": "yarn.lock" in names,
        "pnpm": "pnpm-lock.yaml" in names,
        "php": php,
        "composer": php,
        "python": bool(names & {"Pipfile", "pyproject.toml", "requirements.txt"}),
        "go": "go.mod" in names,
        "rust": "Cargo.toml" in names,
        "docker": bool(names & docker_names) or any(
            _composer_requires_sail(manifest) for manifest in composer_manifests
        ),
        "additional_packages": [],
    }


def apply_recipe_runtime(stack: dict[str, Any], recipe: dict[str, Any]) -> None:
    """Add only the runtime of a complete recipe to the confirmable stack."""
    install = recipe.get("install")
    opening = recipe.get("open")
    if not (isinstance(install, dict) and isinstance(opening, dict)
            and install.get("status") == "complete" and opening.get("status") == "complete"):
        return
    runtime = recipe.get("runtime")
    if not isinstance(runtime, dict) or runtime.get("required") is not True:
        raise SandboxError("complete recipe does not declare a required runtime")
    kind = runtime.get("kind")
    if kind == "node":
        stack["node"] = True
    elif kind != "standalone":
        raise SandboxError(f"unsupported agent runtime: {kind}")


def proposal(root: Path, project_label: str, project: Path, agent: str,
             packages: list[str]) -> tuple[dict[str, Any], dict[str, Any]]:
    base, schema, catalog, template_hash = load_templates(root)
    recipe = read_json(base / "recipes" / f"{agent}.json")
    if not isinstance(recipe, dict) or recipe.get("slug") != agent:
        raise SandboxError(f"recipe is incompatible with the {agent} slot")
    stack = detect_stack(project)
    apply_recipe_runtime(stack, recipe)
    invalid = sorted({package for package in packages if not PACKAGE.fullmatch(package)})
    if invalid:
        raise SandboxError("invalid additional packages: " + ", ".join(invalid))
    stack["additional_packages"] = sorted(set(packages))
    scope = project_label.rsplit("/", 1)[-1]
    schema_version = schema.get("properties", {}).get("schema_version", {}).get("const")
    if not isinstance(schema_version, int):
        raise SandboxError("profile.schema.json does not declare an integer schema_version const")
    payload = {
        "schema_version": schema_version,
        "project": {"name": scope, "absolute_path": str(project)},
        "scope": scope,
        "agent": agent,
        "stack": stack,
        "binds": _binds(catalog, recipe, agent),
    }
    inputs = {"profile": payload, "template_sha256": template_hash,
              "catalog_version": catalog.get("schema_version")}
    confirmation_hash = digest(inputs)
    payload["input_sha256"] = confirmation_hash
    return payload, {"proposal": payload, "confirmation_hash": confirmation_hash}


def validate_binds(binds: list[dict[str, str]]) -> None:
    for bind in binds:
        source = Path(bind["source"])
        if not source.exists():
            raise SandboxError(f"missing bind source: {source}")
        if source.is_socket():
            raise SandboxError(f"host socket cannot be mounted as a bind: {source}")
        expected = bind["kind"]
        valid = source.is_file() if expected == "file" else source.is_dir()
        if not valid:
            raise SandboxError(f"incompatible type for bind {source}: expected {expected}")


def recipe_for(base: Path, agent: str) -> dict[str, Any]:
    recipe = read_json(base / "recipes" / f"{agent}.json")
    if not isinstance(recipe, dict):
        raise SandboxError(f"{agent} recipe must be a JSON object")
    declared = recipe.get("agent", recipe.get("slug", agent))
    if declared != agent:
        raise SandboxError(f"recipe is incompatible with the {agent} slot")
    install = recipe.get("install")
    opening = recipe.get("open")
    if (not isinstance(install, dict) or not isinstance(opening, dict)
            or install.get("status") != "complete" or opening.get("status") != "complete"):
        raise SandboxError(f"{agent} recipe is incomplete; confirmation refused")
    for action in (install, opening):
        argv = action.get("argv")
        if not isinstance(argv, list) or not argv or not all(isinstance(item, str) for item in argv):
            raise SandboxError(f"{agent} recipe does not declare a complete argv")
    return recipe


def output_dir(root: Path, label: str, agent: str) -> Path:
    destination = root / "coding-dockers" / label.rsplit("/", 1)[-1] / agent
    if not _inside(destination.resolve(), root.resolve()):
        raise SandboxError("sandbox destination escapes the scope root")
    return destination


def render(root: Path, payload: dict[str, Any]) -> Path:
    label = payload["scope"]
    agent = payload["agent"]
    base, _, _, _ = load_templates(root)
    recipe = recipe_for(base, agent)
    destination = output_dir(root, label, agent)
    if destination.exists():
        raise SandboxError(f"sandbox already exists: {destination}")
    destination.mkdir(parents=True)
    try:
        for name in (
            "Dockerfile", "entrypoint.sh", "start.sh", "stop.sh", "clean.sh",
            "seccomp-docker.json",
        ):
            shutil.copy2(base / name, destination / name)
        (destination / "recipe.json").write_bytes(canonical(recipe))
        (destination / "profile.json").write_bytes(canonical(payload))
        descriptor = read_json(base / "sandbox.json")
        descriptor.update({
            "status": "ready",
            "identity": {"scope": payload["scope"], "agent": agent,
                         "project_name": payload["project"]["name"]},
            "image": f"pop-{payload['scope']}-{agent}",
            "container": f"pop-{payload['scope']}-{agent}",
            "project": {"source": payload["project"]["absolute_path"],
                        "target": f"/home/coder/{payload['project']['name']}"},
            "stack": payload["stack"],
            "binds": payload["binds"],
            "agent": {"open_argv": recipe["open"]["argv"]},
        })
        (destination / "sandbox.json").write_bytes(canonical(descriptor))
    except Exception:
        shutil.rmtree(destination)
        raise
    return destination


def command_new(args: argparse.Namespace, root: Path) -> int:
    validate_agent(args.agent)
    label, project = resolve_project(root, args.project)
    payload, shown = proposal(root, label, project, args.agent, args.package)
    if args.confirm is None:
        print(json.dumps(shown, ensure_ascii=False, sort_keys=True, indent=2))
        return 0
    if args.confirm != shown["confirmation_hash"]:
        raise SandboxError("confirmation does not exactly match the current proposal")
    validate_binds(payload["binds"])
    destination = render(root, payload)
    print(destination)
    return 0


def command_list(root: Path) -> int:
    base = root / "coding-dockers"
    rows = []
    for profile in sorted(base.glob("**/profile.json")) if base.is_dir() else []:
        try:
            data = read_json(profile)
            rows.append({"project": data["scope"], "agent": data["agent"],
                         "path": str(profile.parent)})
        except (KeyError, TypeError, SandboxError):
            rows.append({"path": str(profile.parent), "status": "invalid"})
    print(json.dumps(rows, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


def check_fresh(root: Path, project_value: str, agent: str) -> int:
    validate_agent(agent)
    label, project = resolve_project(root, project_value)
    profile_path = output_dir(root, label, agent) / "profile.json"
    if not profile_path.is_file():
        raise SandboxError(f"missing profile: {profile_path}")
    saved = read_json(profile_path)
    if not isinstance(saved, dict):
        raise SandboxError(f"invalid profile: {profile_path}")
    packages = saved.get("stack", {}).get("additional_packages", [])
    if not isinstance(packages, list) or not all(isinstance(item, str) for item in packages):
        raise SandboxError(f"invalid profile: {profile_path}")
    current, _ = proposal(root, label, project, agent, packages)
    if saved != current:
        raise SandboxError(f"stale sandbox: {label}/{agent}")
    print(f"fresh: {label}/{agent}")
    return 0


def command_rm(args: argparse.Namespace, root: Path) -> int:
    validate_agent(args.agent)
    label, _ = resolve_project(root, args.project)
    destination = output_dir(root, label, args.agent)
    if not destination.is_dir():
        raise SandboxError(f"missing sandbox: {destination}")
    descriptor = read_json(destination / "sandbox.json")
    if not isinstance(descriptor, dict):
        raise SandboxError("invalid sandbox.json; removal refused")
    try:
        info = subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL, check=False)
    except OSError as exc:
        raise SandboxError("could not prove the absence of Docker resources") from exc
    if info.returncode != 0:
        raise SandboxError("Docker daemon unavailable; absence of resources not proven")
    for kind, name in (("container", descriptor.get("container")),
                       ("image", descriptor.get("image"))):
        if not isinstance(name, str) or not name:
            raise SandboxError(f"invalid {kind} identity; removal refused")
        result = subprocess.run(["docker", kind, "inspect", name],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                check=False)
        if result.returncode == 0:
            raise SandboxError(f"remaining internal resource ({kind} {name}); run clean.sh")
        if result.returncode != 1:
            raise SandboxError(f"could not prove the absence of {kind} {name}")
    project_path = Path(read_json(destination / "profile.json")["project"]["absolute_path"]).resolve()
    if _inside(project_path, destination.resolve()):
        raise SandboxError("invalid profile: project cannot be inside generated artifacts")
    shutil.rmtree(destination)
    print(destination)
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--vault", help=argparse.SUPPRESS)
    result.add_argument("--check-fresh", nargs=2, metavar=("PROJECT", "AGENT"))
    commands = result.add_subparsers(dest="command")
    new = commands.add_parser("new", help="propose or confirm a sandbox")
    new.add_argument("project")
    new.add_argument("agent")
    new.add_argument("--package", action="append", default=[], help="confirmed additional package")
    new.add_argument("--confirm", metavar="HASH", help="exact hash printed by the proposal")
    commands.add_parser("list", help="list local sandboxes")
    remove = commands.add_parser("rm", help="remove only already-cleaned local artifacts")
    remove.add_argument("project")
    remove.add_argument("agent")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    root = poplib.vault_root(args.vault).resolve()
    if poplib.is_installed_scope(root):
        raise SandboxError("coding dockers are unavailable in an installed harness")
    if args.check_fresh:
        return check_fresh(root, *args.check_fresh)
    if args.command == "new":
        return command_new(args, root)
    if args.command == "list":
        return command_list(root)
    if args.command == "rm":
        return command_rm(args, root)
    parser().print_help()
    return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SandboxError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
