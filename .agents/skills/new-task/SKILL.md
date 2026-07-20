---
name: new-task
description: Quick interview that creates a task from a roadmap phase as a folder in pop/kanban/001_initial_task, with the card filled in, specs linked and a link in the epoch. Use when the user asks to start/create a task.
---

# new-task

Materializes a roadmap task as a folder in the kanban, at stage `001_initial_task` — **confirming the essentials with the user before creating**. Full flow: [[WORKFLOW|WORKFLOW]].

**Yolo mode (no interview):** a yolo-scope task (Yolo mode section of the WORKFLOW) is materialized directly by the orchestrator — the answers come from the roadmap (task/phase description, dependencies from the table, `critical` from the project's default); skip the interview and follow the Procedure with the yolo adjustments.

**Delegate to subagents:** almost nothing — it is a short interview with the user; delegation begins at planning (`advance-task`).

## Interview (skip what the user already answered)

1. **Where:** which project and phase? If the user doesn't know, show the in-progress phases of the current epoch and propose the next natural task (from the epoch's candidate table, if any). **Hotfix/one-off fix unrelated to the epoch in progress** (production bug fix, tweak to logic already applied by another epoch): propose `epoch: 0 / phase: 0.1` directly (maintenance Epoch 0 — see [[AGENTS|AGENTS]]) instead of asking for a phase of the current epoch; suggested `size` default `S`.
2. **What and why:** what does the task deliver, in one line? Why now — what does it unblock?
3. **Dependencies:** which tasks must be completed before this one (`depends_on`)? Look at the epoch's tasks and propose; empty = can run in parallel with the others. (Gate: it only enters 004 with all of them completed — see WORKFLOW.)
4. **Criticality:** does this task also require human approval at verification (`critical: true`)? Consider the project's default in the sheet (PROJECT.md).
5. **Specs and research:** which durable contracts does it affect? Link an existing spec; create a draft through `write-spec` only if it introduces durable behavior, interface or invariant. A technical decision without prior research gets a `RESEARCHES.md` prompt before 002.
6. **Size:** does the change fit in **one cohesive brief** (≤~150 lines, preferably much less)? Independent objectives or too many fronts for a readable DAG → propose tasks chained by `depends_on`.
7. **Effort (`size`):** propose `S | M | L` by delivery volume, with one-line rationale. Size alone does not choose topology: risk, skills, dependencies and write sets determine one executor or fronts/waves; planner and reviewer remain separate.
8. Propose the **id and slug** (`<n>.<m>.<t>-<slug>`: `t` is the next free number in the phase; kebab-case slug, unique in the vault) and confirm.

## Procedure

1. Confirm the task exists (or add it) in the phase table in `pop/roadmap/<n>-<epoch-slug>.md`. **Epoch 0:** if `pop/roadmap/0-maintenance.md` doesn't exist yet, create it from `_templates/EPOCH.md` (Status: `continuous`; Description: "One-off fixes and tweaks outside the plan — never completes"; a single Phase `0.1`) and add the Epoch 0 line to the project's `pop/ROADMAP.md`.
2. Create the folder `pop/kanban/001_initial_task/<id>-<slug>/` (the vault-root meta-project and not-yet-migrated projects: harness at the root, no `pop/`) with the card `<id>-<slug>.md` copied from `_templates/TASK.md`:
   - Full frontmatter (`id`, `project`, `epoch`, `phase`, `stage: 001_initial_task`, `critical`, `yolo`, `size`, `blocked: false`, `depends_on: [...]`, `awaiting_merge: false`, dates).
   - **Resolve the yolo inheritance** (epoch → phase → task marker; the ` · yolo: no` opt-out wins): inherited/marked → `yolo: true` + a Log line with the origin (`yolo inherited from phase X.Y`).
   - **Stamp the `size`:** the ` · size:` marker of the task's line in the roadmap, or the interview's suggestion (yolo mode without a marker: suggest it yourself) — always with a 1-line justification in the Log (`size M suggested: <reason>`). The human corrects it freely in 001.
   - "What", "Why", the "Dependencies" section and spec links filled in with the interview answers; first Log line.
   - The **Release** section stays with `- [ ] Ready to plan` **unchecked** — the card is born unreleased. **Exception:** a `yolo: true` task is born **checked**, with Log `released by yolo (marked on the roadmap)`.
3. In the epoch table, turn the task id into the wikilink `[[<id>-<slug>]]` and update the status to `001_initial_task`.
4. If it is the project's first active task, check whether the project status in the INDEX files (category + root) should change to "in progress".
5. Close by pointing at the **release gate**. Explicit “create and advance” may check it with a Log entry and chain to 003; `yolo: true` chains and delegates 003 to the independent reviewer.

## Cautions

- **Read the project's AGENTS.md before creating:** constraints declared there apply — e.g. the organization gate of an imported project (Epoch 1 open → harness tasks only: specs, skills, researches, notes in `pop/`).
- Task files are linked **by name only** (`[[1.1.1-user-table-creation]]`), never by path — the folder moves between stages.
- Don't write the plan here — that happens in `002_planning` via the `advance-task` skill.
