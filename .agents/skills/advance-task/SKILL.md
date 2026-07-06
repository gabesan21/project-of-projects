---
name: advance-task
description: Orchestrates a task's advance through the kanban (001→006), delegating each stage's work to a dedicated subagent and chaining stages until the next human gate. Use when the user asks to advance, plan, execute, verify, or complete a task.
---

# advance-task

You are the **orchestrator**: identify the task's stage, resolve gates and transitions and **advance until the next human gate** — never stop at an agent→agent transition. The source of truth is the [[WORKFLOW|WORKFLOW]]: read **only the section of the stage the task is in + the Cross-cutting rules** — this skill does not rewrite the stages.

**Delegate to subagents:** all the work of 002, 004 and 005 (one dedicated subagent per stage); the orchestrator executes only 001, 006, gates and transitions.

## Input

- **task id** (e.g. `1.1.1-user-table-creation`). Locate the folder: `find <project>/kanban -maxdepth 2 -name "<id>*" -type d`.

## Orchestrator loop

0. **Claim first:** `scripts/pop_claim.py <task-id>` — refused (active claim by another agent)? **Do not touch the task**, report and finish.
1. Read the card: `stage`, `critical`, `blocked`, `depends_on`, the "Skills per stage" table.
2. While there is no pending human gate:
   - Read the current stage's section in the [[WORKFLOW|WORKFLOW]] and execute it — **001 and 006** yourself (they are cheap); **002/004/005** via a dedicated subagent (below).
   - Transition: `scripts/pop_move.py <task-id> <stage>` moves the folder, updates `stage:`/`updated:` and appends the Log line — atomically (without the script, do all three by hand).
3. Upon reaching a gate, **release the claim** (`scripts/pop_claim.py <task-id> --release`), **stop and report**: the current stage, what awaits the human and what the next call will do.

**Human gates (the only stops):** approval at `003`; human verification if `critical: true` at `005`; a subtask `(user)` item; `blocked: true`; the merge round at `006`.

## Subagents per stage

Each subagent receives **only** its stage's skill (the card's "Skills per stage" table) + the minimal context — never the whole vault:

- **002 — planner:** receives the card + linked specs → returns the `.plan.md` (spawns its own wargame recon subagents).
- **004 — executor:** receives the plan + the "Minimal executor context" section → works in the task's worktree, returns checked checkboxes + divergences.
- **005 — verifier:** receives the plan's verification table → returns the `.verify.md` with evidence. **Never the same agent that executed** — it judges without the bias of whoever did the work.

## Cautions (of this skill; the flow's are in the Cross-cutting rules)

- **Never skip stages or gates.** Allowed returns: 003→002, 004→002, 005→004 — the orchestrator decides the return; the subagent only reports.
- A subagent reported an abort, a `(user)` item or a discovery that changes the plan → stop/return per the WORKFLOW; **do not improvise in the main window**.
- When unblocking a task, clear `blocked:` and `blocked_reason:`.
- A learning in 006 **updates an existing note on the same theme** when there is one (don't duplicate); a contradiction with a previous note/decision becomes a visible `> Contradicts: [[target]] — <why>` line.
