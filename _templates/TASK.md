---
id: <n>.<m>.<t>
project: <category>/<project>
epoch: <n>
phase: "<n>.<m>"
stage: 001_initial_task
critical: false
blocked: false
blocked_reason:
depends_on: []
worktree:
pr:
awaiting_merge: false
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# <id>-<slug> — <short title>

- **Phase:** [[<category>/<project>/roadmap/<n>-<epoch-slug>|Phase <n>.<m>]]
- **Plan:** [[<id>-<slug>.plan]] · **Approval:** [[<id>-<slug>.approval]] · **Verification:** [[<id>-<slug>.verify]]

## What

One or two sentences: what this task delivers.

## Why

One sentence: why now, and what it unblocks.

## Skills per stage

> Filled in during 002_planning. Owners per stage: see [[WORKFLOW|WORKFLOW]].

| Stage | Project skills | Owner |
|-------|----------------|-------|
| 004_processing | [[<category>/<project>/skills/<skill>\|<skill>]] | agent |
| 005_verifying | [[<category>/<project>/skills/<skill>\|<skill>]] | agent |

## Dependencies

> Mirrors `depends_on:` in the frontmatter. The task only enters `004_processing` once every dependency is completed (card in `006_done` or `memory/<id>*.md` exists). Empty = can run in parallel with the others.

- [[<id-of-prerequisite-task>]] — what it delivers that this task needs.

## Links

- **Specs:** [[<category>/<project>/specs/<spec>|<spec>]]
- **Related tasks:** [[<id-of-another-task>]]

## Log

- YYYY-MM-DD — created in 001_initial_task — <reason/origin>
