#!/usr/bin/env python3
"""pop_task — scaffolding for a new task in 001_initial_task.

Creates `kanban/001_initial_task/<id>/<id>.md` in the given project from
`_templates/TASK.md`, filling in id, project, epoch, phase, dates and title,
and creates an empty `subtasks/` folder. Refuses if the task already exists
in any project/stage (ids are unique across the vault).

Usage:
    python3 scripts/pop_task.py <category>/<project> <task-id> [--title "..."]
    e.g.: python3 scripts/pop_task.py agents/my-project 1.2.3-user-table-creation
"""

import argparse
import re
import sys

import poplib

TASK_ID = re.compile(r"^(\d+)\.(\d+)\.(\d+)-([a-z0-9][a-z0-9-]*)$")


def fill_template(template, task_id, project, title):
    """Replaces the obvious placeholders of _templates/TASK.md."""
    epoch, phase_n, _, slug = TASK_ID.match(task_id).groups()
    phase = f"{epoch}.{phase_n}"
    numeric_id = task_id.split("-", 1)[0]
    date = poplib.today()
    text = template
    for old, new in (
        ("<n>.<m>.<t>", numeric_id),
        ("<n>.<m>", phase),
        ("<n>", epoch),
        ("<category>/<project>", project),
        ("<id>-<slug>", task_id),
        ("<short title>", title or slug.replace("-", " ")),
        ("created: YYYY-MM-DD", f"created: {date}"),
        ("updated: YYYY-MM-DD", f"updated: {date}"),
        ("- YYYY-MM-DD — created in 001_initial_task — <reason/origin>",
         f"- {date} — created in 001_initial_task — via pop_task"),
    ):
        text = text.replace(old, new)
    return text


def main():
    parser = argparse.ArgumentParser(
        description="Creates the folder and card of a new task in "
                    "kanban/001_initial_task, from _templates/TASK.md.")
    parser.add_argument("project", metavar="CATEGORY/PROJECT",
                        help="destination project (e.g. agents/my-project)")
    parser.add_argument("task_id", metavar="TASK-ID",
                        help="full task id (e.g. 1.2.3-user-table-creation)")
    parser.add_argument("--title", help="short card title "
                                        "(default: slug with spaces)")
    parser.add_argument("--vault", metavar="DIR",
                        help="vault root (default: folder above scripts/)")
    args = parser.parse_args()

    if not TASK_ID.match(args.task_id):
        print(f"Invalid id: {args.task_id} — expected "
              f"<epoch>.<phase>.<task>-<kebab-slug> (e.g. 1.2.3-user-table).")
        return 1

    root = poplib.vault_root(args.vault)
    project_dir = root / "categories" / args.project
    if not (project_dir / "kanban").is_dir():
        print(f"Project without kanban/: {project_dir} — check "
              f"<category>/<project>.")
        return 1
    existing = poplib.find_task(root, args.task_id)
    if existing:
        _, stage, task_dir = existing
        print(f"Task already exists in {stage}: {task_dir}")
        return 1
    template_path = root / "_templates" / "TASK.md"
    if not template_path.is_file():
        print(f"Template not found: {template_path}")
        return 1

    task_dir = project_dir / "kanban" / "001_initial_task" / args.task_id
    task_dir.mkdir(parents=True)
    (task_dir / "subtasks").mkdir()
    card = task_dir / f"{args.task_id}.md"
    card.write_text(
        fill_template(template_path.read_text(encoding="utf-8"),
                      args.task_id, args.project, args.title),
        encoding="utf-8")
    print(f"OK: task created at {card}")
    print("Reminder: fill in 'What', 'Why' and depends_on, and link "
          "[[{}]] in the epoch file.".format(args.task_id))
    print("The task only leaves 001 once the human checks "
          "`- [x] Ready to plan` (Release section of the card).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
