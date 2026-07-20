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
| 002_planning | Link affected durable contracts. Create a draft through `write-spec` only when the task introduces or changes durable behavior, interface or invariant; a fix restoring an existing contract only references it. |
| 003_human_approval | `- [x] Done` also approves any spec changes proposed in the brief: affected drafts move to `approved`. |
| 004_processing | Reality diverged from the spec → record the divergence in the spec's "Open" section and in the card's notes. **Never rewrite the spec silently** — a relevant change goes back to 002. |
| 006_done | **In the same close-out as memory:** update each truly affected spec to reflect delivery. If no durable promise changed, record that in the ledger and invent no edit. Superseded specs become `obsolete` with a replacement link. |

## Audit (on demand or in the weekly-review)

Delegate it to a **subagent** (answer ≤30 lines): list the tasks in `pop/kanban/006_done` and read the specs (`pop/specs/`) their plans link (the vault-root meta-project and not-yet-migrated projects: harness at the root, no `pop/`), flagging **(a)** specs still `draft`/`approved` that don't reflect what the task delivered → pending; **(b)** `obsolete` specs without a link to a replacement, or with no task/phase reference → candidates for archiving/rewriting. The main agent only decides what to do with the list.

## Cautions

- Checking spec impact in 006 **is not optional**; editing a spec without a contract change is noise.
- A spec stores durable behavior, invariants, interfaces, errors and criteria — never reasoning, edit sequences or contingent internal solutions.
- A divergence discovered in 004 is valuable information: record it before it gets lost, even if the decision is deferred.
- When changing a spec's status, also update its links (phase, tasks) if they changed.
