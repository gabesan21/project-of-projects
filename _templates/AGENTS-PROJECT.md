# <Project name> — instructions for agents

> Project managed by the **ProjectOfProjects (PoP)** workflow. `CLAUDE.md` is a symlink to this file — always edit this one.

- **Type:** default | included | multi-repo — see [[TYPES|TYPES]].
- **Project language:** <en> — specs, notes, researches, code comments and the entire kanban flow follow this language.
- **Supported languages (i18n):** <list of languages the application must support — handled in the roadmap and specs. Applications only; remove if not applicable.>
- **Profile:** [[<category>/<project>/PROJECT|PROJECT]] · **Roadmap:** [[<category>/<project>/ROADMAP|ROADMAP]]

## Repositories

| Repo | URL | Clone at | PR branch |
|------|-----|----------|-----------|
| <name> | <url> | `project/<name>/` (default/multi-repo) \| project root (included) | <main> |

_No external repository: the work lives in the PoP repository and task PRs target its main branch._

## Workflow

Every change to the project goes through the kanban (`kanban/001_initial_task → … → 006_done`):

1. **001** — task is born (skill `new-task`), with `depends_on:` listing the prerequisite tasks.
2. **002** — plan with acceptance criteria and linked specs (skills `advance-task`, `write-spec`, `sync-specs`).
3. **003** — human gate: the agent only advances with `- [x] Done`.
4. **004** — execution **in its own worktree** (`worktrees/<id>/`, branch `task/<id>`); it only enters once every `depends_on` has completed.
5. **005** — verification of the criteria in the worktree (+ human approval if `critical: true`).
6. **006** — PR to the PR branch above → **the human merges** → the agent writes `memory/<id>.md`, removes the worktree and finishes.

**One run = one stage:** each agent call executes a single stage, makes one transition and **stops** — continuing requires a new call from the human. Full detail: [[WORKFLOW|WORKFLOW]] (at the PoP root; copied into this repository when the type is `included`).

## Skills

- **PoP workflow:** `.agents/skills/` — `new-task`, `advance-task`, `plan-roadmap`, `write-spec`, `sync-specs`.
- **Project domain:** `skills/` — listed in the profile [[<category>/<project>/PROJECT|PROJECT]].

## DOX process (applications only)

> **Application** projects paste here the full section from [[_templates/DOX|_templates/DOX.md]] — a tree of AGENTS.md files in the code as hierarchical contracts. This AGENTS.md may exceed the ~150 lines to hold it. **Remove this section in all other project types.**

## Essential rules

- Content in en; wikilinks for internal references; files ≤~150 lines; dates YYYY-MM-DD.
- **Never** change the real project outside a task in `004_processing` whose plan was approved in 003.
- **Never** check `- [ ] Done` or execute `(user)` items — those belong exclusively to the human.
- **Never** merge a task PR — merging is the human's job (or commanded by them in the merge round).
- Every completed task produces `memory/<id>.md` (≤2000 chars, final commit, dates) — the `kanban/006_done/` folder can be cleaned; the memory stays.
