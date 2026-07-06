# ProjectOfProjects

> This file is the **AGENTS.md** (the open standard read by Cursor, opencode, Codex, Copilot etc.). `CLAUDE.md` is a symlink to it — always edit this one.

## What this repository is

A second brain for projects — the "project of projects" — organized as an **Obsidian vault**. It catalogs ideas and initiatives of every kind (programming, writing, work, AI agents etc.) that will be developed with the help of AI agents.

This repository **does not contain the projects' code**. It contains each project's planning, tracking and *harness*: the rules, context and instructions an AI agent needs to work on that project.

## Vault structure

```
ProjectOfProjects/
├── AGENTS.md            ← this file: general vault rules (CLAUDE.md → symlink)
├── .agents/skills/      ← the vault's core skills (open SKILL.md format, agent-agnostic)
├── INDEX.md             ← master index: every project, 144 chars each
├── INBOX.md             ← the human's inbox: everything awaiting a decision
├── WORKFLOW.md          ← kanban state machine (task flow)
├── TYPES.md             ← project types: default | included | multi-repo
├── _templates/          ← templates for every standard file
├── notes/               ← vault notes: decisions/ holds the harness decisions
├── scripts/             ← Python CLI (pop_status, pop_move, pop_validate, pop_task, pop_worktree) — saves scanning tokens
├── agents/              ← AI agents, automations, skills
│   ├── INDEX.md         ← category index: 600 chars + status
│   └── <project>/       ← standard anatomy (below)
├── applications/        ← applications and software in general
├── writing/             ← writing: articles, books, content
└── work/                ← professional projects
```

New categories may be created when no existing one fits — always with their own `INDEX.md`, registering the new folder in this file and in the root `INDEX.md`.

## Anatomy of a project

```
<category>/<project>/
├── AGENTS.md            ← standalone instructions: type, repos, workflow (CLAUDE.md → symlink)
├── .agents/skills/      ← real copies of the PoP core workflow skills
├── .gitignore           ← worktrees/ + clones of the project's repos
├── PROJECT.md           ← the sheet: what it is, structure, agent harness
├── ROADMAP.md           ← EPOCHS only: one line + status + link each
├── roadmap/             ← 1 file per epoch: phases and tasks, short descriptions
├── project/             ← the project itself: free structure
├── researches/          ← research that feeds the roadmap: one folder per topic
├── skills/              ← reusable procedures, one per file
├── specs/               ← specifications, one per theme
├── notes/               ← agent and user notes, by category
│   └── learnings/ decisions/ ideas/ references/
├── memory/              ← 1 summary ≤2000 chars per completed task (generated in 006)
├── worktrees/           ← git worktrees of tasks in execution (never committed)
└── kanban/              ← flow stages (see [[WORKFLOW|WORKFLOW]])
    ├── 001_initial_task/
    ├── 002_planning/
    ├── 003_human_approval/
    ├── 004_processing/
    ├── 005_verifying/
    └── 006_done/
```

- **PROJECT.md** — the sheet: what it is, why it exists, harness. It holds no tasks and no schedule.
- **ROADMAP.md + roadmap/** — the path, in three levels with descriptions that are always short (≤1 line):
  - **Epoch** (`1`): a big chapter of the project (e.g. "authentication", "payments"). One line in ROADMAP.md, detail in `roadmap/<n>-<slug>.md`.
  - **Phase** (`1.1`): a stage within the epoch (e.g. "user tables", "middleware"). Listed in the epoch's file.
  - **Task** (`1.1.1-<slug>`): the executable unit. It becomes a **folder in the kanban** and travels through the stages described in [[WORKFLOW|WORKFLOW]].
- **project/** — the real work (code, manuscript etc.), fully free structure; if it lives in an external repository, it contains only a pointer (a note with a link). **researches/** — research that grounds the roadmap: free structure inside one folder per topic; deep-research prompts proposed by the agent for the **user** to run go in `RESEARCHES.md` (optional, next to the ROADMAP — [[_templates/RESEARCHES|template]]).
- **AGENTS.md + .agents/skills/** — make the project **standalone**: type, repositories, PR branch and the essentials of the workflow, with **real copies** of the core skills — even someone who doesn't use the PoP can work on the project. **Application** projects embed the **DOX** process there ([[_templates/DOX|template]]): a tree of AGENTS.md files in the code as hierarchical contracts per subtree.
- **memory/** — durable summary of each completed task (final commit + dates); allows cleaning `006_done` periodically. **worktrees/** — one git worktree per task in execution, always gitignored.
- **skills/** — reusable "how to do X". **specs/** — the detail of each theme.
- **notes/** — notes from the agent **and** the user, with `author: agent | user` frontmatter, in the categories: `learnings/` (lessons from tasks), `decisions/` (decisions extracted from the sheet), `ideas/` (loose ideas) and `references/` (links and external material).

When creating a project, **copy the templates from `_templates/`** and create the empty kanban folders. Don't invent new structures without updating the templates alongside.

## Types and repositories

The PoP is a **repository aggregator**: every project declares a **type** in its AGENTS.md — `default` (work in `project/`, optional repo declared only there), `included` (harness at the root of the project's repo) or `multi-repo` (`project/` with several repos) — detail in [[TYPES|TYPES]]. Repos of `included` and `multi-repo` go in the **Aggregated repositories** section of the root [[INDEX|INDEX]]; clones are never committed to the PoP (`.gitignore`).

## IDs and link convention

- IDs follow the hierarchy: epoch `1` → phase `1.1` → task `1.1.1-user-table-creation`. Slug in kebab-case, unique across the vault (if it collides with another project, adjust the slug).
- **Task files move** between kanban stages, so all of them carry the task's unique name in the file name (`1.1.1-user-table-creation.md`, `1.1.1-user-table-creation.plan.md`…) and are linked **by name only**: `[[1.1.1-user-table-creation]]` resolves in any stage.
- **Files that don't move** (sheets, roadmaps, specs, skills, indexes) are linked with full path + alias: `[[agents/my-project/PROJECT|My Project]]`.
- **Links with a trigger:** in agent-facing navigation sections (the card's Links, related specs, memory, learnings, DOX contracts), every link carries 1 line saying **when** to follow it — a link without a trigger there is a link the agent rightly ignores.

## Indexes and INBOX

- **`INDEX.md` (root):** vault structure + every project, description of **up to 144 characters** each, and the **Aggregated repositories** list (repos to clone, with path and PR branch).
- **`<category>/INDEX.md`:** per project: link, **status** and description of **up to 600 characters**.
- **`INBOX.md` (root):** everything awaiting the human — generated **automatically via Dataview** from the cards' frontmatter (tasks in `003_human_approval`, critical items in `005_verifying`, blocked ones). Don't edit the lists by hand; it is the only file the human needs to open each day.

**Project status:** idea | planning | in progress | paused | completed | abandoned

## Core skills of the vault

The central procedures are **skills** in the open Agent Skills format (`SKILL.md`), in `.agents/skills/` — the **only** skills folder in the vault, agent-agnostic. **Never create tool-specific folders** (`.claude/`, `.cursor/` etc.). Agents without native reading of `.agents/skills/` (Claude Code included): read and follow the corresponding `SKILL.md` before performing the operation.

| Skill | When to use |
|-------|-------------|
| `new-project` | Guided interview that creates a new project: essence, harness, roadmap and specs. |
| `import-project` | Imports an existing repository: recon, fit into type/category and Epoch 1 of organization. |
| `plan-roadmap` | Build/evolve the roadmap by interview (epochs → phases → candidate tasks). |
| `new-task` | Quick interview that materializes a task in `kanban/001_initial_task`. |
| `advance-task` | Move a task through the 001→006 flow, respecting the human gates. |
| `write-spec` | Create/rewrite a standardized spec, with questions per project type. |
| `sync-specs` | Mandatory flow: keep specs faithful to reality as tasks advance. |
| `weekly-review` | Vault overview: what awaits the human, what is stalled, proposals. |
| `excalidraw-diagram` *(optional, external)* | `.excalidraw` diagrams that argue visually — for specs, plans and notes (pairs with the Obsidian Excalidraw plugin). By [coleam00](https://github.com/coleam00/excalidraw-diagram-skill) — clone it into `.agents/skills/excalidraw-diagram/`. |

When creating a new skill: create the folder at `.agents/skills/<name>/SKILL.md` and register it in the table above. When changing a core workflow skill, propagate the copy to the projects' `.agents/skills/` (the `weekly-review` audits the drift). Third-party skills are not edited locally — update them from upstream.

## Rules for agents working in this vault

1. **Language:** the general content of this vault is written in **English by default — forks may adopt any language**. Each project declares its **default language** in its own AGENTS.md — specs, notes, research, code comments and that project's entire flow follow the declared language (applications also declare the languages supported for i18n).
2. **It is an Obsidian vault:** use wikilinks `[[...]]` for every internal reference, following the link convention above.
3. **Cross-reference whenever needed:** when mentioning another project, spec, skill, task or note, link it. Related projects cite each other.
4. **One project, one folder, inside a category:** never mix material from different projects. Every project folder follows the standard anatomy.
5. **Modularization — no file too large:** a note must not exceed **~150 lines** (exceptions: a task's `.plan.md`, up to **200** — see [[WORKFLOW|WORKFLOW]] — and the AGENTS.md of an **application** project, which embeds the DOX process). When approaching the limit, extract sections into their own files and leave a wikilink with a one-line summary. A file answers **one** question; if it answers two, it is two files. Roadmap descriptions are always one line — detail goes to a spec or a task.
6. **One run = up to the next human gate:** the agent advances the task and only stops where a human decision is awaited — gates and orchestration in [[WORKFLOW|WORKFLOW]].
7. **Explicit owner:** every stage, subtask and skill has a declared owner (`agent` or `user`) and the agent never executes a `(user)` item — table and rules in [[WORKFLOW|WORKFLOW]].
8. **Indexes always in sync:** when creating, completing or changing a project's status, update the category `INDEX.md` **and** the root one. Respect the limits: 144 chars (root), 600 chars (category).
9. **Absolute dates:** always YYYY-MM-DD, never "next week" or "last month".
10. **Decisions are recorded:** important decisions made in conversation go into the project folder (with date and rationale) before ending the session.
11. **Lessons are extracted:** when completing a task, whatever was learned and is reusable becomes a skill (`skills/`) or a note (`notes/`), linked in the task's card.
12. **Planning and execution don't mix:** each project's real work lives exclusively in `project/` — or in the external repository indicated in the sheet's harness, with `project/` holding only the pointer. The other folders are for planning and knowledge.
13. **Every change to the project goes through the kanban:** agents **never** touch `project/` (or the external repository) outside a task in `004_processing` with a plan approved in 003 — no "quick fix"; detail in [[WORKFLOW|WORKFLOW]].
14. **Self-validation before finishing:** the agent checks its own changes from the session — index limits (144/600 chars), ~150 lines per note, complete frontmatter on cards, links following the convention — and fixes anything out of bounds before the commit.
15. **Commit per session:** this vault is a git repository. When ending a work session, commit the changes with a short message in the vault's language saying what changed.
16. **One worktree per task, merge by the human:** 004 work happens in the task's worktree, PR in 006 and merge **by the human only**; 004 requires completed `depends_on` — detail in [[WORKFLOW|WORKFLOW]].
17. **Durable memory:** every completed task generates `memory/<id>.md` (≤2000 chars) before finishing — `006_done` may be cleaned, the memory counts as proof; detail in [[WORKFLOW|WORKFLOW]].
18. **Delegation by default:** broad context reading (recon, audits, sweeps, DOX tree walks, skill diffs) never happens in the main agent's window — it goes to a subagent that receives (a) a specific question, (b) the relevant skill/section, (c) a response format with a cap (e.g. ≤30 lines). The main agent orchestrates and decides.

## Harness decisions

The vault's architecture decisions live in `notes/decisions/`, one note per decision day — consult them before proposing harness changes: [[notes/decisions/2026-07-04-harness-decisions|2026-07-04]] · [[notes/decisions/2026-07-05-harness-decisions|2026-07-05]] · [[notes/decisions/2026-07-06-harness-decisions|2026-07-06]].

## Open decisions (to discuss)

_None at the moment._
