# Approval — [[<id>-<slug>]]

> Blockquotes are filling instructions — **delete them when filling**.

- **Stage:** 003_human_approval · **Owner:** user | independent reviewer in yolo

> One round per visit to 003. The gate approves the brief, not reasoning or implementation details. Never delete old rounds. In `yolo: true`, replace the human subsection with `### Reviewer response (yolo)`, preserve the checkbox and use an auditable signature.

## Round 1 — YYYY-MM-DD

### Decision brief

- **Delivery:** <one line>.
- **Strategy:** <one or two lines>.
- **Topology:** <single executor or fronts/waves>.
- **Main risk:** <material risk or none>.
- **Main criteria:** <IDs or short summary>.
- **Plan:** [[<id>-<slug>.plan]] — *follow to review the complete brief*.

### Human response

_(write here: approved, or what to change)_

- [ ] Done

### Agent decision

_(after Done: `approved → 004` or `changes requested → 002: <summary>`)_

## Merge — 006 — YYYY-MM-DD

> Created when the applicable flow requires human merge. In yolo, follow [[WORKFLOW|WORKFLOW]] integration policy; do not invent another quality gate here.

- **PR:** <link> — `task/<id>-<slug>` → `<PR branch>`.
- _Without git: record the applicable final approval._

### Human response

_(merge, or explicitly authorize the agent)_

- [ ] Done

### Agent decision

_(final commit, generated memory, removed worktree and closed task)_
