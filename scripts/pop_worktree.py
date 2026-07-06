#!/usr/bin/env python3
"""pop_worktree — creates/removes a task's git worktree.

`add` creates `worktrees/<task-id>` in the task's project folder, with the
branch `task/<task-id>`, in the given repository (`--repo`; default: vault
root). `remove` undoes the worktree and deletes the branch if it is already
merged (`--delete-branch` forces the deletion).

Usage:
    python3 scripts/pop_worktree.py add    <task-id> [--repo DIR] [--base BRANCH]
    python3 scripts/pop_worktree.py remove <task-id> [--repo DIR] [--delete-branch]
"""

import argparse
import subprocess
import sys

import poplib


def git(repo, *args):
    """Runs git in the repo; returns CompletedProcess (does not raise)."""
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True)


def fail(action, result):
    """Reports the git failure in a readable way and returns exit code 1."""
    detail = (result.stderr or result.stdout).strip() or "no details"
    print(f"Failed to {action} (git exit {result.returncode}):\n  {detail}")
    return 1


def cmd_add(repo, worktree, branch, base):
    """git worktree add worktrees/<id> -b task/<id> [<base>]."""
    if worktree.exists():
        print(f"Worktree already exists: {worktree}")
        return 1
    worktree.parent.mkdir(parents=True, exist_ok=True)
    args = ["worktree", "add", str(worktree), "-b", branch]
    if base:
        args.append(base)
    result = git(repo, *args)
    if result.returncode != 0:
        return fail(f"create the worktree {worktree}", result)
    print(f"OK: worktree {worktree} created on branch {branch}"
          + (f" from {base}." if base else "."))
    print(f"Reminder: record `worktree: worktrees/{worktree.name}` in the "
          f"card's frontmatter.")
    return 0


def cmd_remove(repo, worktree, branch, force_delete):
    """git worktree remove + deletes the branch if merged (or with --delete-branch)."""
    result = git(repo, "worktree", "remove", str(worktree))
    if result.returncode != 0:
        return fail(f"remove the worktree {worktree}", result)
    print(f"OK: worktree {worktree} removed.")

    merged = git(repo, "branch", "--merged")
    is_merged = merged.returncode == 0 and any(
        line.strip().lstrip("* ") == branch
        for line in merged.stdout.splitlines())
    if is_merged or force_delete:
        flag = "-D" if force_delete else "-d"
        result = git(repo, "branch", flag, branch)
        if result.returncode != 0:
            return fail(f"delete the branch {branch}", result)
        print(f"OK: branch {branch} deleted"
              + (" (forced)." if force_delete and not is_merged else "."))
    else:
        print(f"Branch {branch} kept (not merged — use --delete-branch "
              f"to force).")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Creates or removes a task's git worktree "
                    "(worktrees/<id>, branch task/<id>).")
    parser.add_argument("action", choices=["add", "remove"],
                        help="add: creates worktree and branch; remove: undoes")
    parser.add_argument("task_id", help="task id (folder name in the kanban)")
    parser.add_argument("--repo", metavar="DIR",
                        help="target git repository (default: vault root)")
    parser.add_argument("--base", metavar="BRANCH",
                        help="starting branch for the new branch (add only)")
    parser.add_argument("--delete-branch", action="store_true",
                        help="on remove, deletes the branch even if unmerged")
    parser.add_argument("--vault", metavar="DIR",
                        help="vault root (default: folder above scripts/)")
    args = parser.parse_args()

    root = poplib.vault_root(args.vault)
    found = poplib.find_task(root, args.task_id)
    if not found:
        print(f"Task not found in any project: {args.task_id}")
        return 1
    project, stage, _ = found
    print(f"Task {args.task_id} in {poplib.project_label(root, project)} "
          f"({stage}).")

    repo = poplib.vault_root(args.repo) if args.repo else root
    if not (repo / ".git").exists():
        print(f"Not a git repository: {repo}")
        return 1
    worktree = project / "worktrees" / args.task_id
    branch = f"task/{args.task_id}"
    if args.action == "add":
        return cmd_add(repo, worktree, branch, args.base)
    return cmd_remove(repo, worktree, branch, args.delete_branch)


if __name__ == "__main__":
    sys.exit(main())
