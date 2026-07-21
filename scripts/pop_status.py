#!/usr/bin/env python3

import argparse
import datetime
import sys

import poplib

WIP_LIMIT = 3
STALE_DAYS = 14


def _stale_since(meta):
    raw = str(meta.get("updated") or "")
    try:
        updated = datetime.date.fromisoformat(raw)
    except ValueError:
        return None
    return (datetime.date.today() - updated).days


def collect(project):
    counts = {stage: 0 for stage in poplib.STAGES}
    attention = {"release": [], "approval": [], "critical": [], "merge": [],
                 "blocked": [], "circuit": [], "stale": [], "claimed": []}
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
        if meta.get("circuit_breaker") is True:
            r003 = meta.get("yolo_003_returns") or 0
            r005 = meta.get("yolo_005_returns") or 0
            attention["circuit"].append(
                f"{tid} — returns 003={r003}, 005={r005}")
        if stage != "006_done":
            days = _stale_since(meta)
            if days is not None and days > STALE_DAYS:
                attention["stale"].append(f"{tid} — not updated for {days} days")
        by, at = poplib.parse_claim(meta)
        if by and stage != "006_done":
            when = at.isoformat(timespec="minutes") if at else "?"
            mark = "" if not poplib.claim_expired(at) else " [EXPIRED]"
            attention["claimed"].append(f"{tid} — {by} since {when}{mark}")
    return counts, attention


def print_project(label, counts, attention):
    total = sum(counts.values())
    print(f"\n## {label} — {total} task(s)")
    for stage in poplib.STAGES:
        if counts[stage]:
            print(f"  {stage}: {counts[stage]}")
    if total == 0:
        print("  (empty kanban)")
    if counts["004_processing"] > WIP_LIMIT:
        print(f"  [WARNING] WIP in 004_processing: {counts['004_processing']} "
              f"(limit {WIP_LIMIT})")


def print_list(title, items):
    if not items:
        return
    print(f"\n{title}:")
    for item in items:
        print(f"  - {item}")


def main():
    parser = argparse.ArgumentParser(
        description="Vault overview: tasks by stage and pending gates.")
    parser.add_argument("--project", metavar="CATEGORY/PROJECT",
                        help="limit output to one project")
    parser.add_argument("--vault", metavar="DIR",
                        help="vault root (default: directory above scripts/)")
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
        print("No project with a kanban found in the vault.")
        return 0

    merged = {"release": [], "approval": [], "critical": [], "merge": [],
              "blocked": [], "circuit": [], "stale": [], "claimed": []}
    print(f"Vault: {root}")
    for project in projects:
        label = poplib.project_label(root, project)
        counts, attention = collect(project)
        print_project(label, counts, attention)
        for key, items in attention.items():
            merged[key].extend(f"{tid} ({label})" for tid in items)

    print_list("Waiting for human release (001, without "
               "`- [x] Ready to plan`)", merged["release"])
    print_list("Waiting for human approval (003)", merged["approval"])
    print_list("Pending critical verification (005, critical)", merged["critical"])
    print_list("Waiting for merge (awaiting_merge)", merged["merge"])
    print_list("Blocked", merged["blocked"])
    print_list("Yolo circuit breakers (human intervention)", merged["circuit"])
    print_list(f"Stale (not updated for >{STALE_DAYS} days, outside 006)",
               merged["stale"])
    print_list("In progress (active claim — do not take these tasks)",
               merged["claimed"])
    if not any(merged.values()):
        print("\nNothing is waiting for the human.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
