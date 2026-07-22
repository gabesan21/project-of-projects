#!/usr/bin/env python3

import argparse
import shutil
import sys

import poplib

RETURNS = {
    ("003_human_approval", "002_planning"),
    ("004_processing", "002_planning"),
    ("005_verifying", "004_processing"),
}


def transition_allowed(src, dst, *, yolo_single_gate=False):
    """True when dst is src's next stage or a permitted return.

    `yolo_single_gate` (non-critical yolo task) allows the 002→004 jump:
    yolo's single quality gate is 005 (see the WORKFLOW's Yolo mode section).
    """
    stages = poplib.STAGES
    if stages.index(dst) == stages.index(src) + 1:
        return True
    if yolo_single_gate and (src, dst) == ("002_planning", "004_processing"):
        return True
    return (src, dst) in RETURNS


def update_card(card, new_stage, reason, fields=None):
    lines = card.read_text(encoding="utf-8").splitlines()
    date = poplib.today()
    fields = fields or {}
    found = set()
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                end = i
                break
            key = lines[i].split(":", 1)[0].strip()
            if key == "stage":
                lines[i] = f"stage: {new_stage}"
            elif key == "updated":
                lines[i] = f"updated: {date}"
            elif key in fields:
                lines[i] = f"{key}: {fields[key]}"
                found.add(key)
        for key, value in fields.items():
            if key not in found:
                lines.insert(end, f"{key}: {value}")
    card.write_text(append_log(lines, f"- {date} — {reason}") + "\n",
                    encoding="utf-8")


def append_log(lines, entry):
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
        description="Move a task folder to another kanban stage and update "
                    "the card frontmatter and log.")
    parser.add_argument("task_id", help="task ID (folder name, for example "
                                        "1.1.1-user-table-creation)")
    parser.add_argument("stage", choices=poplib.STAGES,
                        help="destination stage")
    parser.add_argument("--reason", default="transition via pop_move",
                        help="short reason recorded in the card log")
    parser.add_argument("--context", action="append", default=[],
                        help="agent context used at this stage; repeatable")
    parser.add_argument("--test-seconds", type=float, default=0,
                        help="test time associated with this transition")
    parser.add_argument("--by", default=poplib.default_agent(),
                        help="agent identifier (default: user@host; same as pop_claim)")
    parser.add_argument("--force", action="store_true",
                        help="allow a nonstandard transition and override claim/release")
    parser.add_argument("--vault", metavar="DIR",
                        help="vault root (default: directory above scripts/)")
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
    card_src = task_dir / f"{args.task_id}.md"
    meta = poplib.read_card(card_src) if card_src.is_file() else {}
    yolo_single_gate = (meta.get("yolo") is True
                        and meta.get("critical") is not True)
    if (not transition_allowed(src, args.stage,
                               yolo_single_gate=yolo_single_gate)
            and not args.force):
        print(f"Transition not allowed: {src} → {args.stage}. "
              f"Flow: 001→002→003→004→005→006 (non-critical yolo: 002→004 "
              f"directly, no 003); returns: 003→002, 004→002, 005→004. "
              f"Use --force for exceptions.")
        return 1

    if card_src.is_file() and not args.force:
        by, at = poplib.parse_claim(meta)
        if by and by != args.by and not poplib.claim_expired(at):
            print(f"CLAIMED: {args.task_id} has an active claim by {by} since "
                  f"{at.isoformat(timespec='minutes')} — do not move another "
                  f"agent's task (use --force for exceptions).")
            return 1
        if (src == "001_initial_task" and args.stage == "002_planning"
                and meta.get("yolo") is not True
                and not poplib.task_released(card_src)):
            print(f"NOT RELEASED: {args.task_id} does not yet have "
                  f"`- [x] Ready to plan` in the card's Release section — "
                  f"the human releases stage 001 (use --force for exceptions).")
            return 1

    return_gate = None
    if (src, args.stage) == ("003_human_approval", "002_planning"):
        return_gate = "003"
    elif (src, args.stage) == ("005_verifying", "004_processing"):
        return_gate = "005"
    fields = {}
    if meta.get("yolo") is True and return_gate:
        key = f"yolo_{return_gate}_returns"
        try:
            attempts = int(meta.get(key) or 0)
        except (TypeError, ValueError):
            attempts = 0
        if attempts >= poplib.YOLO_RETURN_LIMIT and not args.force:
            reason = (f"yolo circuit breaker at {return_gate}: the third "
                      "failure requires human diagnosis")
            update_card(card_src, src, reason, {
                "blocked": "true", "blocked_reason": reason,
                "circuit_breaker": "true"})
            poplib.record_telemetry(task_dir, {
                "event": "circuit_breaker", "stage": src,
                "gate": return_gate, "contexts": args.context,
                "test_seconds": args.test_seconds, "result": "blocked"})
            print(f"BLOCKED: {args.task_id} — {reason}.")
            return 1
        fields[key] = attempts + 1

    dest_dir = poplib.harness_root(project) / "kanban" / args.stage
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / args.task_id
    if dest.exists():
        print(f"Destination already exists: {dest}")
        return 1
    shutil.move(str(task_dir), str(dest))

    card = dest / f"{args.task_id}.md"
    if card.is_file():
        update_card(card, args.stage, f"{src}→{args.stage} — {args.reason}", fields)
        poplib.record_telemetry(dest, {
            "event": "transition", "from": src, "to": args.stage,
            "contexts": args.context, "test_seconds": args.test_seconds,
            "result": "returned" if return_gate else "advanced"})
    else:
        print(f"[WARNING] card not found for update: {card}")
    print(f"OK: {args.task_id} ({label}) moved {src} → {args.stage}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
