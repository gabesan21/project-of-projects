# <Project name> — instructions for agents

> Blockquotes in this template are fill-in instructions — **delete them when filling it in** (except the one below, which stays in the project).

> Project managed by the **ProjectOfProjects (PoP)** workflow. `CLAUDE.md` is a symlink to this file — always edit this one.

- **Type:** default | included | multi-repo | full-multi-repo — see [[TYPES|TYPES]].
- **Project language:** <en> — specs, notes, researches, code comments and the entire kanban flow follow this language.
- **Supported languages (i18n):** <list of languages the application must support — handled in the roadmap and specs. Applications only; remove if not applicable.>
- **Profile:** [[categories/<category>/<project>/pop/PROJECT|PROJECT]] · **Roadmap:** [[categories/<category>/<project>/pop/ROADMAP|ROADMAP]]

## Repositories

| Repo | URL | Clone at | PR branch |
|------|-----|----------|-----------|
| <name> | <url> | `<name>/` at the project root (default/multi-repo/full-multi-repo) \| the project root **is** the repo (included) | <main> |

_No external repository: the work lives in the PoP repository and task PRs target its main branch._

> **`full-multi-repo`:** each embedded repo has its **own AGENTS.md** (type `included`) with a **"Part of"** section linking this parent project, the general ROADMAP and the cross-repo kanban. Specs and memory live only in the repos — see [[TYPES|TYPES]].

## Workflow

Every change to the project goes through the kanban (`pop/kanban/001_initial_task → … → 006_done`):

1. **001** — task is born (skill `new-task`), with `depends_on:` listing the prerequisite tasks.
2. **002** — plan with acceptance criteria and linked specs (skills `advance-task`, `write-spec`, `sync-specs`).
3. **003** — human gate: the agent only advances with `- [x] Done`.
4. **004** — execution **in its own worktree** (`pop/worktrees/<id>/`, branch `task/<id>`); it only enters once every `depends_on` has completed.
5. **005** — verification of the criteria in the worktree (+ human approval if `critical: true`).
6. **006** — PR to the PR branch above → **the human merges** → the agent writes `pop/memory/<id>.md`, removes the worktree and finishes.

**One run = up to the next human gate:** the agent acts as an orchestrator — a dedicated subagent per stage — and chains stages until a gate: approval in 003, verification if `critical`, a `(user)` item, a block, or the merge round in 006. Full detail: [[WORKFLOW|WORKFLOW]] (at the PoP root; copied into this repository when the type is `included`).

## Context protocol

1. Start from the card and the plan: read **only** what they list.
2. Missing context → a subagent with a specific question, never "read the folder to get familiar".
3. Stop searching once you can answer *what changes and where* — anything beyond that is overthinking.
4. A doubt the search did not resolve = **RECON NEEDED** in the plan or `blocked:` on the card — never an assumption.
5. Specs and memory exist so the past is never reread: consult them before any git/code archaeology.

## Skills

- **PoP workflow:** `.agents/skills/` — `new-task`, `advance-task`, `plan-roadmap`, `write-spec`, `sync-specs`.
- **Project domain:** `pop/skills/` — listed in the profile [[categories/<category>/<project>/pop/PROJECT|PROJECT]].

### Clean code (code projects only)

> **Remove this section if the project is not a code project.**

- `clean-code-change` (`.agents/skills/`) — follow when **planning (002) and executing (004)** any task that creates or changes code.
- `clean-code-review` (`.agents/skills/`) — follow when **verifying (005)** a code task and as a reading criterion in plan or PR gates.
- **Mandatory:** in 002, every task that creates/changes code enters `clean-code-change` on the **004** row and `clean-code-review` on the **005** row of the card's **Skills per stage** table.

#### Project verification

> Exact commands the clean code skills run — keep faithful to the project's real tooling.

| Check | Command |
|-------|---------|
| Formatter | `<command>` |
| Linter | `<command>` |
| Tests | `<command>` |

## DOX process (applications only)

> **Application** projects paste here the full section from [[_templates/DOX|_templates/DOX.md]] — a tree of AGENTS.md files in the code as hierarchical contracts. This AGENTS.md may exceed the ~150 lines to hold it. **Remove this section in all other project types.**

## Essential rules

- Content in en; wikilinks for internal references; files ≤~150 lines; dates YYYY-MM-DD.
- **Never** change the real project outside a task in `004_processing` whose plan was approved in 003.
- **Never** check `- [ ] Done` or execute `(user)` items — those belong exclusively to the human.
- **Never** merge a task PR — merging is the human's job (or commanded by them in the merge round).
- Every completed task produces `pop/memory/<id>.md` (≤2000 chars, final commit, dates) — the `pop/kanban/006_done/` folder can be cleaned; the memory stays.
