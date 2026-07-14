---
id: <n>.<m>.<t>
project: <category>/<project>
epoch: <n>
phase: "<n>.<m>"
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
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# <id>-<slug> — <short title>

> Blockquotes in this template are fill-in instructions — **delete them when filling it in**. Harness paths carry the `pop/` prefix — on claim (004), `worktree:` receives `pop/worktrees/<id>-<slug>` (in the vault-root meta-project: without the `pop/` prefix).

- **Phase:** [[categories/<category>/<project>/pop/roadmap/<n>-<epoch-slug>|Phase <n>.<m>]]
- **Plan:** [[<id>-<slug>.plan]] · **Approval:** [[<id>-<slug>.approval]] · **Verification:** [[<id>-<slug>.verify]]

## What

One or two sentences: what this task delivers.

## Why

One sentence: why now, and what it unblocks.

## Release (user)

> Only the human checks it (or the agent, **under an explicit command** from the human, recording it in the Log). Without `[x]`, the task doesn't leave 001 — the card is yours to edit; `pop_move` refuses 001→002. **Yolo exception:** a `yolo: true` task is born with the checkbox checked by the agent — the roadmap mark is the early release (Log: `released by yolo (marked on the roadmap)`); see the Yolo mode section of [[WORKFLOW|WORKFLOW]].

- [ ] Ready to plan

## Skills per stage

> The 002 row is filled in at task creation (001); the 004/005 rows are filled in during 002_planning. Owners per stage: see [[WORKFLOW|WORKFLOW]].

| Stage | Project skills | Owner |
|-------|----------------|-------|
| 002_planning | [[categories/<category>/<project>/pop/skills/<skill>\|<skill>]] | agent |
| 004_processing | [[categories/<category>/<project>/pop/skills/<skill>\|<skill>]] | agent |
| 005_verifying | [[categories/<category>/<project>/pop/skills/<skill>\|<skill>]] | agent |

## Dependencies

> Mirrors `depends_on:` in the frontmatter. The task only enters `004_processing` once every dependency is completed — an existing `pop/memory/<id>*.md` is the standard signal (the folder in `006_done` is deleted on close); a card still in `006_done` also counts, for the short window before deletion. Empty = can run in parallel with the others.

- [[<id-of-prerequisite-task>]] — what it delivers that this task needs.

## Links

> Every link carries a 1-line trigger — *when* it is worth following. A link without a trigger is rightly ignored.

- **Specs:** [[categories/<category>/<project>/pop/specs/<spec>|<spec>]] — *follow if <condition>*.
- **Related tasks:** [[<id-of-another-task>]] — *follow if <condition>*.

## Log

- YYYY-MM-DD — created in 001_initial_task — <reason/origin>
