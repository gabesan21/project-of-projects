# Epoch <n> — <epoch name>

> Blockquotes in this template are fill-in instructions — **delete them when filling it in**.

- **Project:** [[categories/<category>/<project>/pop/PROJECT|<Project name>]] · **Roadmap:** [[categories/<category>/<project>/pop/ROADMAP|Roadmap]]
- **Status:** pending | in progress | completed (or **continuous** — reserved for the Epoch 0 of maintenance, see [[AGENTS|AGENTS]]: never completes, the `weekly-review` doesn't chase it for stagnation)
- **Description:** one line — what this chapter delivers.
- **Yolo:** yes | no — **optional** bullet (absent = no); only the human marks it.
- **Abort/pause if:** objective condition, if any (audited by the `weekly-review`).

> One phase per section; under each phase, only still-open tasks — **always one-line descriptions**. In 006, remove a task row only after its canonical memory is valid; preserve the epoch, phase, and other open tasks.
> **Yolo inherits:** a yolo epoch → phases and tasks inherit; a yolo phase → tasks inherit. Per-task opt-out/opt-in: append ` · yolo: no` (or ` · yolo: yes`) to the end of the Description cell — no new column. `new-task` resolves the inheritance and stamps the card (Yolo mode section of [[WORKFLOW|WORKFLOW]]).
> **Size:** the agent suggests `S|M|L` in the Description; `new-task` stamps it on the card and the human corrects it in 001. Size guides tier/effort; risk, skills, dependencies and write sets determine topology in [[WORKFLOW|WORKFLOW]].

## Recon and forks

> Researches in `pop/researches/` (in the vault-root meta-project: without the `pop/` prefix) that grounded the breakdown; whatever remained unanswered is RECON NEEDED, with the check that resolves it. Forks: pre-identified route changes.

- [[categories/<category>/<project>/pop/researches/<topic>/<note>|<topic>]] — what it established, in one line.
- [ ] RECON NEEDED: <assumption> — check: <research/experiment/task that resolves it>.
- Fork: if <observation/conclusion X> → <what changes in the epoch, in one line>.

## Phase <n>.1 — <phase name>

- **Status:** pending | in progress | completed
- **Description:** one line.
- **Yolo:** yes | no — **optional** bullet (absent = inherits from the epoch).
- **Specs:** [[categories/<category>/<project>/pop/specs/<spec>|<spec>]]

| Task | Description (≤1 line) | Status |
|------|-----------------------|--------|
| `<n>.1.1-<slug>` | What it delivers. · size: M | not started |
| [[<n>.1.2-<slug>]] | What it delivers (linked: already exists in the kanban). | 002_planning |

## Phase <n>.2 — <phase name>

- **Status:** pending
- **Description:** one line.

| Task | Description (≤1 line) | Status |
|------|-----------------------|--------|
| `<n>.2.1-<slug>` | ... | not started |
