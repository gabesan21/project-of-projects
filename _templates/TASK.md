---
id: <n>.<m>.<t>
project: <category>/<project>
origin: roadmap
epoch: <n>
phase: "<n>.<m>"
modification:
stage: 001_initial_task
critical: false
yolo: false
size: S | M | L
blocked: false
blocked_reason:
depends_on: []
claimed_by:
claimed_at:
worktree:
pr:
awaiting_merge: false
yolo_003_returns: 0
yolo_005_returns: 0
circuit_breaker: false
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# <id>-<slug> — <short title>

> Blockquotes in this template are fill-in instructions — **delete them when filling it in**. Harness paths carry the `pop/` prefix; the vault-root meta-project does not.
> **Origin:** a roadmap task (`origin: roadmap`) uses id `<n>.<m>.<t>` and fills `epoch`/`phase` (delete `modification`); a modification task (`origin: modifications`) uses id `M-<n>.<t>` and fills `modification: M-<n>` (delete `epoch`/`phase`).

- **Origin:** [[categories/<category>/<project>/pop/roadmap/<n>-<epoch-slug>|Phase <n>.<m>]] — *or* [[categories/<category>/<project>/pop/MODIFICATIONS|M-<n>]] for a modification task.
- **Plan:** [[<id>-<slug>.plan]] · **Approval:** [[<id>-<slug>.approval]] · **Verification:** [[<id>-<slug>.verify]]

## What

One or two sentences about the observable delivery, without anticipating implementation.

## Why

One sentence: why now, and what it unblocks.

## Release (user)

> Only the human checks it, except under an explicit command recorded in the Log. Without `[x]`, the task does not leave 001. For `yolo: true`, the roadmap/modifications release lets the agent check and log `released by yolo`; see [[WORKFLOW|WORKFLOW]].

- [ ] Ready to plan

## Skills per stage

> Fill 002 at creation and 004/005 during planning. List only skills that change how the owner should work.

| Stage | Project skills | Owner |
|-------|----------------|-------|
| 002_planning | [[categories/<category>/<project>/pop/skills/<skill>\|<skill>]] | agent |
| 004_processing | [[categories/<category>/<project>/pop/skills/<skill>\|<skill>]] | agent |
| 005_verifying | [[categories/<category>/<project>/pop/skills/<skill>\|<skill>]] | agent |

## Dependencies

> Mirrors `depends_on:`. A missing dependency blocks execution; it does not authorize the agent to implement it. Empty = no kanban prerequisite.

- [[<id-of-prerequisite-task>]] — delivery required to start this task.

## Links

> Every link carries a trigger: when it is worth following.

- **Spec:** [[categories/<category>/<project>/pop/specs/<spec>|<spec>]] — *follow to understand <contract/invariant>*.
- **Related task:** [[<id-of-another-task>]] — *follow if <condition>*.

## Log

- YYYY-MM-DD — created in 001_initial_task — <reason/origin>

## Minimal telemetry

> One row per completed/returned stage. Record observable cost, never reasoning, prompts, or discarded attempts.

| Stage | Contexts | Returns | Tests/strategy | Result |
|-------|----------|---------|----------------|--------|
| 002 | planner: 1 | 0 | n/a | plan created |
