---
name: new-task
description: Quick interview that creates a task from a roadmap phase as a folder in kanban/001_initial_task, with the card filled in, specs linked and a link in the epoch. Use when the user asks to start/create a task.
---

# new-task

Materializes a roadmap task as a folder in the kanban, at stage `001_initial_task` — **confirming the essentials with the user before creating**. Full flow: [[WORKFLOW|WORKFLOW]].

**Delegate to subagents:** almost nothing — it is a short interview with the user; delegation begins at planning (`advance-task`).

## Interview (skip what the user already answered)

1. **Where:** which project and phase? If the user doesn't know, show the in-progress phases of the current epoch and propose the next natural task (from the epoch's candidate table, if any).
2. **What and why:** what does the task deliver, in one line? Why now — what does it unblock?
3. **Dependencies:** which tasks must be completed before this one (`depends_on`)? Look at the epoch's tasks and propose; empty = can run in parallel with the others. (Gate: it only enters 004 with all of them completed — see WORKFLOW.)
4. **Criticality:** does this task also require human approval at verification (`critical: true`)? Consider the project's default in the sheet (PROJECT.md).
5. **Specs:** which specs does it affect? Topic without a spec → offer to create a draft with the `write-spec` skill (mandatory before the plan goes to 003 — see `sync-specs`).
6. **Size:** does the change fit in **one** wargame plan (≤200 lines — see WORKFLOW)? If it has too many fronts, **propose splitting into more than one task**, chained via `depends_on` — better N lean boards than one bloated plan.
7. Propose the **id and slug** (`<n>.<m>.<t>-<slug>`: `t` is the next free number in the phase; kebab-case slug, unique in the vault) and confirm.

## Procedure

1. Confirm the task exists (or add it) in the phase table in `roadmap/<n>-<epoch-slug>.md`.
2. Create the folder `kanban/001_initial_task/<id>-<slug>/` with the card `<id>-<slug>.md` copied from `_templates/TASK.md`:
   - Full frontmatter (`id`, `project`, `epoch`, `phase`, `stage: 001_initial_task`, `critical`, `blocked: false`, `depends_on: [...]`, `awaiting_merge: false`, dates).
   - "What", "Why", "Dependencies" section and spec links filled in with the interview answers; first Log line.
3. In the epoch table, turn the task id into the wikilink `[[<id>-<slug>]]` and update the status to `001_initial_task`.
4. If it is the project's first active task, check whether the project status in the INDEX files (category + root) should change to "in progress".
5. Close by offering to **chain straight into planning** via the `advance-task` skill: since one run goes **until the next human gate**, creating the task can proceed to 002 and stop at the `.approval.md` in 003 in the same call — if the user prefers, stop here and leave the advance for another call.

## Cautions

- **Read the project's AGENTS.md before creating:** constraints declared there apply — e.g. the organization gate of an imported project (Epoch 1 open → harness tasks only: specs, skills, researches, notes).
- Task files are linked **by name only** (`[[1.1.1-user-table-creation]]`), never by path — the folder moves between stages.
- Don't write the plan here — that happens in `002_planning` via the `advance-task` skill.
