---
name: advance-task
description: Orchestrates a task's advance through the kanban (001→006), delegating each stage's work to a dedicated subagent and chaining stages until the next human gate. Use when the user asks to advance, plan, execute, verify, or complete a task.
---

# advance-task

You are the **orchestrator**: identify the task's stage, resolve gates and transitions and **advance until the next human gate** — never stop at an agent→agent transition (see Turn discipline). The source of truth is the [[WORKFLOW|WORKFLOW]]: read **only the section of the stage the task is in + the Cross-cutting rules** — this skill does not rewrite the stages.

**Delegate to subagents:** all the work of 002, 004 and 005 (one dedicated subagent per stage); the orchestrator executes only 001, 006, gates and transitions.

## Input

- **task id** (e.g. `1.1.1-user-table-creation`). Locate the folder: `find <project>/pop/kanban -maxdepth 2 -name "<id>*" -type d` (the vault-root meta-project and not-yet-migrated projects: harness at the root, no `pop/`).

## Orchestrator loop

0. **Claim first:** `scripts/pop_claim.py <task-id>` — refused (active claim by another agent)? **Do not touch the task**, report and finish.
1. Read the card: `stage`, `critical`, `yolo`, `size`, `blocked`, `depends_on`, the "Skills per stage" table. **Task in 001 without `- [x] Ready to plan`?** That's a human gate: release the claim, stop and report — the card still belongs to the human. Exceptions: the human explicitly commanded in this conversation to proceed right away → check the box on their behalf and record it in the Log (`released by human command`); `yolo: true` → the roadmap mark is the release — check it with Log `released by yolo (marked on the roadmap)`.
2. While there is no pending human gate:
   - Read the current stage's section in the [[WORKFLOW|WORKFLOW]] and execute it — **001 and 006** yourself (they are cheap); **002/004/005** via a dedicated subagent (below). **Fast path (`size: S`):** execute **002** yourself (mini-plan ≤40 lines — section 002 of the WORKFLOW) and **004**, recording the fast path in the Log; **005 remains a subagent** (fresh eyes are not waived).
   - Transition: `scripts/pop_move.py <task-id> <stage> --reason "short reason — contexts: <subagents launched in the stage>"` moves the folder, updates `stage:`/`updated:` and appends the Log line — atomically. **Do not** write a manual line duplicating the script's (without the script, do all three by hand in a single line).
3. Upon reaching a gate, **release the claim** (`scripts/pop_claim.py <task-id> --release`), **stop and report**: the current stage, what awaits the human and what the next call will do.

**Human gates (the only stops):** release at `001` (`- [x] Ready to plan`); approval at `003`; human verification if `critical: true` at `005`; a subtask `(user)` item; `blocked: true`; the merge round at `006`.

**`yolo: true` task** (Yolo mode section of the [[WORKFLOW|WORKFLOW]]): the gates at 001, 003, `critical` at 005 and the task integration in 006 are resolved by the **critic** subagent ([[.agents/skills/yolo-critic/SKILL|yolo-critic]]) — no PR and no `pr:`/`awaiting_merge:` per task; the only human stops are a `(user)` item, `blocked: true` and the final scope review. **Scope loop:** once a yolo-scope task completes, materialize the next eligible task of the phase/epoch (`new-task` without an interview, in `depends_on` order, WIP 3 prioritized by you) until the scope is done — then the scope close-out (a delivery open question, **no automatic PR** — protocol in the critic's skill; a single-task scope closes at the end of that task itself). A yolo mark removed mid-flight takes effect at the next gate.

## Turn discipline

"Chaining stages within a single call" has mechanical consequences — the violations below were observed in the field and are **orchestrator bugs**, not stops:

- **Stage delegation is synchronous:** when launching the 002/004/005/critic subagent, **wait for its result before anything else**. If the harness runs subagents in the background by default, use the synchronous/blocking mode; if only active waiting is available, wait until it completes. "No subagent has completed yet" is not a final state — it is a signal that the wait continues. Launching ≠ delegating: a stage whose result was not collected is a stage **not executed**.
- **Never end the turn with a stage subagent running.**
- **Last-message test:** if it describes future work owned by `agent` ("I'll keep chaining…", "next I will…"), the turn **cannot end** — do that work now. Legitimate endings: a human gate reached (list below), `blocked: true`, or a yolo scope closed (close-out done, not promised).
- **The yolo scope loop runs within the same turn:** once a task completes, materialize and advance the next eligible one in the same run, until the scope ends, `blocked` or a `(user)` item. Progress reporting happens at the close-out — it is not a stopping point.

## Subagents per stage

Each subagent receives **only** its stage's skill (the card's "Skills per stage" table) + the minimal context — never the whole vault. Every stage subagent's contract includes: **no web** (a knowledge gap → prompt in `RESEARCHES.md` + `blocked`, section 002 of the WORKFLOW), a **response cap** ("write the file, return the path + a summary ≤10 lines") and the **model by tier** from the role × size matrix of the Orchestration (`scripts/models.json`):

- **002 — planner:** receives the card + linked research and specs → returns the `.plan.md` (spawns its own **budgeted** recon wave — only questions above rule 18's floor become workers, **0 is valid**, waves of up to 3-5; workers are leaves — they report "Gaps / Not found", never spawn subagents).
- **004 — executor:** receives the plan + the "Minimal executor context" section → works in the task's worktree (`pop/worktrees/<id>`), returns checked checkboxes + divergences.
- **005 — verifier:** receives the plan's verification table → returns the `.verify.md` with evidence. **Never the same agent that executed** — it judges without the bias of whoever did the work.
- **003/critical-005/006 yolo — critic:** receives the card + `.plan.md` + `.approval.md` (critical 005: + `.verify.md` and the worktree; 006: + `.verify.md` and the `task/<id>` branch) → signs the round/verification or sends it back with reasons (skill [[.agents/skills/yolo-critic/SKILL|yolo-critic]]; cap of 2 send-backs in 003; 006 = local merge into `develop`, no PR). Distinct from planner/executor/verifier.

## Cautions (of this skill; the flow's are in the Cross-cutting rules)

- **Never skip stages or gates.** Allowed returns: 003→002, 004→002, 005→004 — the orchestrator decides the return; the subagent only reports.
- **Another agent's active claim covers the task's whole folder** (card, `.plan.md`, `.verify.md`, `subtasks/`): reading ok, writing forbidden — `pop_move` also refuses the transition.
- A subagent reported an abort, a `(user)` item or a discovery that changes the plan → stop/return per the WORKFLOW; **do not improvise in the main window**.
- When unblocking a task, clear `blocked:` and `blocked_reason:`.
- A learning in 006 **updates an existing note on the same theme** when there is one (don't duplicate); a contradiction with a previous note/decision becomes a visible `> Contradicts: [[target]] — <why>` line.
