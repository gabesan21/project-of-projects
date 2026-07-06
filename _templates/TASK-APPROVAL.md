# Approval — [[<id>-<slug>]]

> Blockquotes in this template are fill-in instructions — **delete them when filling it in**.

- **Stage:** 003_human_approval · **Owner:** user

> One round per trip to `003_human_approval`. The agent only acts when `- [x] Done` — see [[WORKFLOW|WORKFLOW]]. Old rounds are never deleted.

## Round 1 — YYYY-MM-DD

### Plan summary

3–5 lines: what will be done, main acceptance criteria, risks. Full plan: [[<id>-<slug>.plan]].

### Human response

_(write here: approved, or what to change)_

- [ ] Done

### Agent decision

_(filled in after the Done: "approved → 004" or "changes requested → 002: <summary of the request>")_

## Merge round — 006 — YYYY-MM-DD

> Final round, created when the task reaches `006_done` with an open PR. The merge is **always the human's** — done directly in the repository, or commanded here for the agent to execute.

- **PR:** <link> — branch `task/<id>-<slug>` → `<PR branch from the project's AGENTS.md>`
- _No git repository: this round is the final approval of the deliverable, without a PR._

### Human response

_(merge it yourself, or write "go ahead and merge" + instructions)_

- [ ] Done

### Agent decision

_(after the merge: final commit, `memory/<id>.md` generated, worktree removed, task closed)_
