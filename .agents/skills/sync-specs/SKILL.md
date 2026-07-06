---
name: sync-specs
description: Mandatory spec-update flow as tasks advance through the kanban - specs can never diverge from the project's reality. Use when planning (002), executing (004) and completing (006) tasks, and to audit outdated specs.
---

# sync-specs

**Principle: a spec describes the project's current agreed state. A lying spec is a bug.** This flow is mandatory and tracks the [[WORKFLOW|WORKFLOW]] stages.

**Delegate to subagents:** the audit (listing 006_done + reading the linked specs); the kanban touchpoints run inside the stage's subagent (`advance-task`).

## Kanban touchpoints

| Stage | Spec obligation |
|-------|-----------------|
| 002_planning | The plan **assembles the change specs**: every affected spec linked in the "Change specs" section and, for a topic without a spec, a draft created (`write-spec` skill) already reflecting what the plan intends to change. A plan without its specs assembled is not ready for 003. |
| 003_human_approval | The `- [x] Done` also approves the spec changes proposed in the plan → affected specs move from `draft` to `approved`. |
| 004_processing | Reality diverged from the spec → record the divergence in the spec's "Open" section and in the card's notes. **Never rewrite the spec silently** — a relevant change goes back to 002. |
| 006_done | **In the same close-out in which the memory is written:** update each affected spec to reflect **what was actually done** — resolve the pertinent "Open" items, adjust requirements and details, status → `implemented` (or keep `approved` if the task covered only part). A superseded spec → `obsolete`, with a link to the replacement. |

## Audit (on demand or in the weekly-review)

Delegate it to a **subagent** (answer ≤30 lines): list the tasks in `006_done` and read the specs their plans link, flagging **(a)** specs still `draft`/`approved` that don't reflect what the task delivered → pending; **(b)** `obsolete` specs without a link to a replacement, or with no task/phase reference → candidates for archiving/rewriting. The main agent only decides what to do with the list.

## Cautions

- Updating specs in 006 **is not optional** — it is part of the task's completion criterion.
- A divergence discovered in 004 is valuable information: record it before it gets lost, even if the decision is deferred.
- When changing a spec's status, also update its links (phase, tasks) if they changed.
