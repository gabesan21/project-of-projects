#!/usr/bin/env python3
"""pop_move — moves a task between kanban stages.

Finds the task folder in any project/stage, validates the transition
(001→002→003→004→005→006, returns 003→002, 004→002 and 005→004; `--force`
allows exceptions), moves the whole folder, updates `stage:` and `updated:`
in the card's frontmatter and records the line in `## Log`.

Locks (overridden only with `--force`): a task with an active claim by
**another** agent doesn't move (`--by` identifies the caller, default
user@host); 001→002 requires the human release `- [x] Ready to plan`
on the card — or `yolo: true` in the frontmatter (the roadmap mark is
the early release; see the Yolo mode section of the WORKFLOW). The claim
also applies to yolo tasks.

Usage:
    python3 scripts/pop_move.py <task-id> <stage> [--reason "..."]
                                [--by NAME] [--force]
"""

import argparse
import shutil
import sys

import poplib

RETURNS = {
    ("003_human_approval", "002_planning"),
    ("004_processing", "002_planning"),
    ("005_verifying", "004_processing"),
}


def transition_allowed(src, dst):
    """True if dst is the next stage after src or an allowed return."""
    stages = poplib.STAGES
    if stages.index(dst) == stages.index(src) + 1:
        return True
    return (src, dst) in RETURNS


def update_card(card, new_stage, reason):
    """Updates stage:/updated: in the frontmatter and appends to ## Log."""
    lines = card.read_text(encoding="utf-8").splitlines()
    date = poplib.today()
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                break
            key = lines[i].split(":", 1)[0].strip()
            if key == "stage":
                lines[i] = f"stage: {new_stage}"
            elif key == "updated":
                lines[i] = f"updated: {date}"
    card.write_text(append_log(lines, f"- {date} — {reason}") + "\n",
                    encoding="utf-8")


def append_log(lines, entry):
    """Inserts the entry at the end of the ## Log section (creates it if missing)."""
    try:
        start = next(i for i, l in enumerate(lines) if l.strip() == "## Log")
    except StopIteration:
        return "\n".join(lines).rstrip("\n") + f"\n\n## Log\n\n{entry}"
    end = next((j for j in range(start + 1, len(lines))
                if lines[j].startswith("## ")), len(lines))
    last = end - 1
    while last > start and not lines[last].strip():
        last -= 1
    lines.insert(last + 1, entry)
    return "\n".join(lines).rstrip("\n")


def main():
    parser = argparse.ArgumentParser(
        description="Moves a task's folder to another kanban stage, "
                    "updating the card's frontmatter and Log.")
    parser.add_argument("task_id", help="task id (folder name, e.g. "
                                        "1.1.1-user-table-creation)")
    parser.add_argument("stage", choices=poplib.STAGES,
                        help="destination stage")
    parser.add_argument("--reason", default="transition via pop_move",
                        help="short reason recorded in the card's Log")
    parser.add_argument("--by", default=poplib.default_agent(),
                        help="agent identifier (default: user@host; same as "
                             "pop_claim)")
    parser.add_argument("--force", action="store_true",
                        help="allows a transition outside the standard flow "
                             "and overrides claim/release locks")
    parser.add_argument("--vault", metavar="DIR",
                        help="vault root (default: folder above scripts/)")
    args = parser.parse_args()

    root = poplib.vault_root(args.vault)
    found = poplib.find_task(root, args.task_id)
    if not found:
        print(f"Task not found in any project: {args.task_id}")
        return 1
    project, src, task_dir = found
    label = poplib.project_label(root, project)
    if src == args.stage:
        print(f"Task {args.task_id} is already in {src} ({label}).")
        return 1
    if not transition_allowed(src, args.stage) and not args.force:
        print(f"Transition not allowed: {src} → {args.stage}. "
              f"Flow: 001→002→003→004→005→006; returns: 003→002, "
              f"004→002, 005→004. Use --force for exceptions.")
        return 1

    card_src = task_dir / f"{args.task_id}.md"
    if card_src.is_file() and not args.force:
        meta = poplib.read_card(card_src)
        by, at = poplib.parse_claim(meta)
        if by and by != args.by and not poplib.claim_expired(at):
            print(f"BUSY: {args.task_id} has an active claim by {by} since "
                  f"{at.isoformat(timespec='minutes')} — don't move another "
                  f"agent's task (use --force for exceptions).")
            return 1
        if (src == "001_initial_task" and args.stage == "002_planning"
                and meta.get("yolo") is not True
                and not poplib.task_released(card_src)):
            print(f"NOT RELEASED: {args.task_id} doesn't have "
                  f"`- [x] Ready to plan` on the card yet (Release section) — "
                  f"the human releases the exit from 001 (use --force for "
                  f"exceptions).")
            return 1

    dest_dir = project / "kanban" / args.stage
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / args.task_id
    if dest.exists():
        print(f"Destination already exists: {dest}")
        return 1
    shutil.move(str(task_dir), str(dest))

    card = dest / f"{args.task_id}.md"
    if card.is_file():
        update_card(card, args.stage, f"{src}→{args.stage} — {args.reason}")
    else:
        print(f"[WARNING] card not found for update: {card}")
    print(f"OK: {args.task_id} ({label}) moved {src} → {args.stage}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
