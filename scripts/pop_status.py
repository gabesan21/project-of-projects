#!/usr/bin/env python3
"""pop_status — overview of the PoP vault.

Shows, per project, the task count per kanban stage and the lists that
require human attention: awaiting release (001), awaiting approval (003),
critical review (005 + critical), awaiting merge, blocked, and a
WIP > 3 alert in 004. Tasks with `yolo: true` are left out of the
approval/review/merge lists — those judgments are delegated to the independent
reviewer (Yolo mode section of the WORKFLOW).

Usage:
    python3 scripts/pop_status.py [--project <category>/<project>] [--vault DIR]
"""

import argparse
import datetime
import sys

import poplib

WIP_LIMIT = 3
STALE_DAYS = 14


def _stale_since(meta):
    """Days since `updated:`, or None if absent/invalid."""
    raw = str(meta.get("updated") or "")
    try:
        updated = datetime.date.fromisoformat(raw)
    except ValueError:
        return None
    return (datetime.date.today() - updated).days


def collect(project):
    """Collects counts and attention lists for a project."""
    counts = {stage: 0 for stage in poplib.STAGES}
    attention = {"release": [], "approval": [], "critical": [], "merge": [],
                 "blocked": [], "stale": [], "claimed": []}
    for stage, task_dir, card in poplib.iter_cards(project):
        counts[stage] += 1
        meta = poplib.read_card(card)
        tid = task_dir.name
        if stage == "001_initial_task" and not poplib.task_released(card):
            attention["release"].append(tid)
        yolo = meta.get("yolo") is True
        if stage == "003_human_approval" and not yolo:
            attention["approval"].append(tid)
        if stage == "005_verifying" and meta.get("critical") is True and not yolo:
            attention["critical"].append(tid)
        if meta.get("awaiting_merge") is True and not yolo:
            attention["merge"].append(tid)
        if meta.get("blocked") is True:
            reason = meta.get("blocked_reason") or "no reason recorded"
            attention["blocked"].append(f"{tid} — {reason}")
        if stage != "006_done":
            days = _stale_since(meta)
            if days is not None and days > STALE_DAYS:
                attention["stale"].append(f"{tid} — no update for {days} days")
        by, at = poplib.parse_claim(meta)
        if by and stage != "006_done":
            when = at.isoformat(timespec="minutes") if at else "?"
            mark = "" if not poplib.claim_expired(at) else " [EXPIRED]"
            attention["claimed"].append(f"{tid} — {by} since {when}{mark}")
    return counts, attention


def print_project(label, counts, attention):
    """Prints a project's block."""
    total = sum(counts.values())
    print(f"\n## {label} — {total} task(s)")
    for stage in poplib.STAGES:
        if counts[stage]:
            print(f"  {stage}: {counts[stage]}")
    if total == 0:
        print("  (empty kanban)")
    if counts["004_processing"] > WIP_LIMIT:
        print(f"  [ALERT] WIP in 004_processing: {counts['004_processing']} "
              f"(limit {WIP_LIMIT})")


def print_list(title, items):
    """Prints an attention list, if not empty."""
    if not items:
        return
    print(f"\n{title}:")
    for item in items:
        print(f"  - {item}")


def main():
    parser = argparse.ArgumentParser(
        description="Vault overview: tasks per stage and pending gates.")
    parser.add_argument("--project", metavar="CATEGORY/PROJECT",
                        help="limits to one project (e.g. agents/my-project)")
    parser.add_argument("--vault", metavar="DIR",
                        help="vault root (default: folder above scripts/)")
    args = parser.parse_args()

    root = poplib.vault_root(args.vault)
    projects = poplib.discover_projects(root)
    if args.project:
        projects = [p for p in projects
                    if poplib.project_label(root, p) == args.project]
        if not projects:
            print(f"Project not found: {args.project}")
            return 1
    if not projects:
        print("No project with a kanban found in the vault — all clear.")
        return 0

    merged = {"release": [], "approval": [], "critical": [], "merge": [],
              "blocked": [], "stale": [], "claimed": []}
    print(f"Vault: {root}")
    for project in projects:
        label = poplib.project_label(root, project)
        counts, attention = collect(project)
        print_project(label, counts, attention)
        for key, items in attention.items():
            merged[key].extend(f"{tid} ({label})" for tid in items)

    print_list("Awaiting human release (001, without "
               "`- [x] Ready to plan`)", merged["release"])
    print_list("Awaiting human approval (003)", merged["approval"])
    print_list("Critical verification pending (005, critical)", merged["critical"])
    print_list("Awaiting merge (awaiting_merge)", merged["merge"])
    print_list("Blocked", merged["blocked"])
    print_list(f"Stale (no update for >{STALE_DAYS} days, outside 006)",
               merged["stale"])
    print_list("In progress (active claim — do not pick these tasks)",
               merged["claimed"])
    if not any(merged.values()):
        print("\nNothing awaiting the human.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
