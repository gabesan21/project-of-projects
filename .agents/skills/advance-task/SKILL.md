---
name: advance-task
description: Moves a task through the kanban flow (001→006), performing the current stage's work and respecting the human gates. Use when the user asks to advance, plan, execute, verify, or complete a task.
---

# advance-task

Performs **one** stage transition of a task according to the WORKFLOW.md state machine (vault root). Read WORKFLOW.md before acting — it is the source of truth; this summary does not replace it. **One call = one stage:** do the current stage's work, move the folder once, and **stop** — the next stage only runs when the agent is called again.

## Input

- **task id** (e.g. `1.1.1-user-table-creation`). Locate the folder with `find <project>/kanban -maxdepth 2 -name "<id>*" -type d` or an equivalent search.

## Procedure

1. Read the card: `stage`, `critical`, `blocked`, the "Skills per stage" table. Do the stage's work and only then move — **a single transition per call**:
   - **001 → 002**: **wargame** — you plan the execution for another executor to run without asking anything. Recon first, read-only, **always with parallel subagents** (one per front; essential on research-heavy boards). Then the `.plan.md` (`_templates/TASK-PLAN.md`, ≤200 lines): route, forks with trigger, abort conditions, RECON NEEDED with check, criteria table with run and pass. Groups in `subtasks/` (`_templates/SUBTASKS.md`): each `(agent)` move with "Expect to see" and "If it fails" (failure → cause → counter-move). **Assemble the change specs** (draft via `write-spec`; see `sync-specs`). **Red-team** the plan and record attack+patch — skippable only for a trivial task with very few steps. Task too big for 200 lines → propose splitting it into more tasks (`depends_on`). Fill in the card's "Skills per stage" table (004/005).
   - **002 → 003**: check the WORKFLOW **readiness gate** (moves with observation/counter-move, forks with trigger, aborts, verification with runs, specs assembled, red-team, executable blind) → create/update `.approval.md` (`_templates/TASK-APPROVAL.md`) with a new round and `- [ ] Done`.
   - **003 → 004 or 002**: **only act if `- [x] Done`** — otherwise, stop and report that it awaits the human. Feedback requests changes → go back to 002; approved → 004. Fill in "Agent decision". **Dependencies:** only move to 004 with every `depends_on` task completed (card in `006_done` **or** `memory/<id>*.md` exists); pending → report and wait. **WIP:** if the project already has 3 tasks in 004, warn and ask which to prioritize.
   - **004 → 005**: **on entry, create the task's worktree** — `git worktree add worktrees/<id> -b task/<id>` in the repository declared in the project's AGENTS.md (`multi-repo`: one per affected repo); record `worktree:` on the card and **work only inside it**. Execute the groups respecting `Depends on:`/`(after ...)` — with no pending prerequisite you may parallelize — checking each move's **expected observation** (applications: follow the **DOX process** in the project's AGENTS.md — walk the code's AGENTS.md tree before editing and update the affected contracts on close-out); failed → the plan's counter-move; fork trigger → pre-authorized route; abort condition (or a situation with no planned route) → stop, `blocked: true` + reason, **do not improvise**. `(user)` item: stop and report. Discovery that changes the plan → back to 002 (new approval cycle). Everything done → 005.
   - **005 → 006 or 004**: create `.verify.md` (`_templates/TASK-VERIFY.md`) from the plan's table and execute **each run**, comparing against the "Pass looks like", **in the worktree**. Failure → back to 004 with notes. If `critical: true`, wait for the human `- [x] Done` in the approval section before advancing.
   - **006**: open the **PR** (`task/<id>` → the PR branch from the project's AGENTS.md), record `pr:` + `awaiting_merge: true` on the card, create the **Merge** round in `.approval.md` and **stop** — the merge belongs to the human (direct or commanded there; without a git repo, the round is the final approval). After the merge: write `memory/<id>.md` (`_templates/MEMORY.md`: summary ≤2000 chars, final commit, start/end dates), remove the worktree (`git worktree remove`), clear `awaiting_merge:`/`worktree:` and, **in the same close-out**, sync the change specs with the project's specs (`sync-specs`) — mandatory, part of completion. Then: derived status — task completed in the epoch; the phase completes if all its tasks completed; the epoch likewise; INDEX if the project changed status. Extract learnings into the project's `skills/` or `notes/learnings/` (`_templates/NOTE.md` template, `author: agent`) and link them on the card.
2. Every transition: `mv` the whole folder to the new stage + update `stage:` and `updated:` in the frontmatter + a line in the card's Log (`YYYY-MM-DD — 002→003 — short reason`). The INBOX derives from the frontmatter via Dataview — do not edit it.
3. Once the transition is done, **stop and report** the new stage and what comes next — do not chain the next stage into this same call.

## Cautions

- **Never skip stages.** Allowed returns: 003→002, 004→002, 005→004.
- **Never chain stages:** even with no human gate on the way (e.g. a freshly completed 004→005), one call never makes two transitions — report and wait for a new call.
- **Never mark `- [ ] Done` nor execute a `(user)` item** — those belong exclusively to the human.
- **Never merge a task PR on your own** — only the human merges, or commands the merge in the merge round.
- Changes to the real project: always inside the task's worktree, never on the main branch.
- Task file links: by name only, never by path.
- When unblocking a task, clear `blocked:` and `blocked_reason:`.
