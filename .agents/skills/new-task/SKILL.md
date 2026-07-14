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
5. **Specs and research:** which specs does it affect? Topic without a spec → offer to create a draft with the `write-spec` skill (mandatory before the plan goes to 003 — see `sync-specs`). A **technical-decision task without research** in `pop/researches/` grounding it → **suggest the prompt in `RESEARCHES.md`** before releasing it to 002 (the planner does no web research — section 002 of the WORKFLOW).
6. **Size:** does the change fit in **one** wargame plan (≤200 lines — see WORKFLOW)? If it has too many fronts, **propose splitting into more than one task**, chained via `depends_on` — better N lean boards than one bloated plan.
7. **Effort (`size`):** **propose** `S | M | L` by complexity (S = fast path: mini-plan and execution by the orchestrator; M/L = the WORKFLOW's Orchestration ceremony), justifying in 1 line — the user confirms or corrects, and can adjust it later on the card in 001.
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
5. Close by pointing at the **release gate**: the card stays in 001 waiting for the human to edit it and check `- [x] Ready to plan` (Release section) — the advance to 002 (`advance-task`) only happens after that. **Exceptions:** the user explicitly commanded in the conversation to proceed right away ("create it and advance") → check the box on their behalf, record it in the Log (`released by human command`) and chain into `advance-task` up to the `.approval.md` in 003; a `yolo: true` task → chain straight into `advance-task` (the 003 gate belongs to the critic).

## Cautions

- **Read the project's AGENTS.md before creating:** constraints declared there apply — e.g. the organization gate of an imported project (Epoch 1 open → harness tasks only: specs, skills, researches, notes in `pop/`).
- Task files are linked **by name only** (`[[1.1.1-user-table-creation]]`), never by path — the folder moves between stages.
- Don't write the plan here — that happens in `002_planning` via the `advance-task` skill.
