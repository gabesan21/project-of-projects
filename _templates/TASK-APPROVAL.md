# Approval — [[<id>-<slug>]]

> Blockquotes in this template are fill-in instructions — **delete them when filling it in**.

- **Stage:** 003_human_approval · **Owner:** user

> One round per trip to `003_human_approval`. The agent only acts when `- [x] Done` — see [[WORKFLOW|WORKFLOW]]. Old rounds are never deleted.
> **Yolo task:** the round uses `### Critic response (yolo)` instead of "Human response" — same `- [ ] Done`, signed `approved by critic agent (yolo) — YYYY-MM-DD` ([[.agents/skills/yolo-critic/SKILL|yolo-critic]]). Never reuse the human subsection: who signed each round must stay auditable. Cap of **2 send-backs** by the critic; the 3rd trip to 003 becomes `blocked: true`. If the human intervenes, they write in their own "Human response" subsection — it prevails and resets the cap.

## Round 1 — YYYY-MM-DD

### Plan summary

3–5 lines: what will be done, main acceptance criteria, risks. Full plan: [[<id>-<slug>.plan]].

### Human response

_(write here: approved, or what to change)_

- [ ] Done

### Agent decision

_(filled in after the Done: "approved → 004" or "changes requested → 002: <summary of the request>")_

## Merge round — 006 — YYYY-MM-DD

> Final round, created when the task reaches `006_done` with an open PR. The merge is **always the human's** — done directly in the repository, or commanded here for the agent to execute. **Yolo task:** the PR targets `develop` and the critic merges it (`### Critic response (yolo)` subsection); the scope's final PR (`develop` → PR branch) is **always the human's**, via an open question — see [[WORKFLOW|WORKFLOW]].

- **PR:** <link> — branch `task/<id>-<slug>` → `<PR branch from the project's AGENTS.md>`
- _No git repository: this round is the final approval of the deliverable, without a PR._

### Human response

_(merge it yourself, or write "go ahead and merge" + instructions)_

- [ ] Done

### Agent decision

_(after the merge: final commit, `memory/<id>.md` generated, worktree removed, task closed)_
