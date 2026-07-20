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
├── TYPES.md             ← project types: default | included | multi-repo | full-multi-repo
├── specs/               ← durable contracts for this harness
├── _templates/          ← templates for every standard file
├── notes/               ← vault notes: decisions/ holds the harness decisions
├── researches/          ← the PoP's own deep researches (raw source in raw/, synthesis alongside)
├── scripts/             ← Python CLI (`pop_*`): status, transitions, validation, worktrees and front ownership
├── open_questions/      ← the agent's questions to the human, outside any task ([[_templates/OPEN-QUESTION|template]])
├── drafts/              ← project drafts filled in by the human
│   ├── new/             ← filled-in copies of [[_templates/NEW_PROJECT|NEW_PROJECT]]
│   └── import/          ← filled-in copies of [[_templates/IMPORT_PROJECT|IMPORT_PROJECT]]
└── categories/          ← every project category
    ├── agents/          ← AI agents, automations, skills
    │   ├── INDEX.md     ← category index: 600 chars + status
    │   └── <project>/   ← standard anatomy (below)
    ├── applications/    ← applications and software in general
    ├── writing/         ← writing: articles, books, content
    └── work/            ← professional projects
```

New categories may be created inside `categories/` when no existing one fits — always with their own `INDEX.md`, registering the new folder in this file and in the root `INDEX.md`.

## Anatomy of a project

```
categories/<category>/<project>/
├── AGENTS.md            ← standalone instructions: type, repos, workflow (CLAUDE.md → symlink)
├── .agents/skills/      ← real copies of the PoP core workflow skills
├── .gitignore           ← pop/worktrees/ + clones of the project's repos
├── pop/                 ← ALL of the PoP harness, in a single folder
│   ├── PROJECT.md       ← the sheet: what it is, structure, agent harness
│   ├── ROADMAP.md       ← EPOCHS only: one line + status + link each
│   ├── roadmap/         ← 1 file per epoch: phases and tasks, short descriptions
│   ├── researches/      ← research that feeds the roadmap: one folder per topic
│   ├── skills/          ← reusable procedures, one per file
│   ├── specs/           ← specifications, one per theme
│   ├── notes/           ← agent and user notes, by category
│   │   └── learnings/ decisions/ ideas/ references/
│   ├── memory/          ← 1 summary ≤2000 chars per completed task (generated in 006)
│   ├── worktrees/       ← git worktrees of tasks in execution (never committed)
│   └── kanban/          ← flow stages (see [[WORKFLOW|WORKFLOW]])
│       ├── 001_initial_task/ 002_planning/ 003_human_approval/
│       └── 004_processing/ 005_verifying/ 006_done/
└── <project content>     ← code, manuscript etc., directly at the root: free structure
```

The dev who opens the project sees only the content, `AGENTS.md`, `.agents/` and `pop/`. **Exception:** projects created **before 2026-07-14** use the legacy anatomy (harness at the folder's root, content in `project/`) until migration — the `pop_*` scripts support both.

- **PROJECT.md** — the sheet: what it is, why it exists, harness. It holds no tasks and no schedule.
- **ROADMAP.md + roadmap/** — the path, in three levels with descriptions that are always short (≤1 line):
  - **Epoch** (`1`): a big chapter of the project (e.g. "authentication", "payments"). One line in ROADMAP.md, detail in `roadmap/<n>-<slug>.md`.
  - **Phase** (`1.1`): a stage within the epoch (e.g. "user tables", "middleware"). Listed in the epoch's file.
  - **Task** (`1.1.1-<slug>`): the executable unit. It becomes a **folder in the kanban** and travels through the stages described in [[WORKFLOW|WORKFLOW]].
  - **Epoch 0 (maintenance, reserved):** hotfixes and one-off tweaks to already-applied logic don't enter the narrative epoch in progress — they go to **Epoch 0**, created **on demand** (on the first task of this kind, by `new-task`) with Status **continuous** (never completes) and a single Phase `0.1`, with no chapter detail — just the running list of tasks.
- **Content at the root** — the real work (code, manuscript, repo clones), a fully free structure; if it lives in an external repository, the root holds only the harness and the repo is declared in the project's AGENTS.md. The names `pop` and `project` are **reserved** (don't use them for a content folder or repo). **researches/** — research that grounds the roadmap: one folder per topic, with the immutable raw source in `raw/` and the agent's synthesis alongside (skill `ingest-research`); deep-research prompts proposed by the agent for the **user** to run go in `RESEARCHES.md` (optional, next to the ROADMAP — [[_templates/RESEARCHES|template]]). **Research is always prior:** the agent does not search the web during the task flow — a knowledge gap becomes a prompt in `RESEARCHES.md` (section 002 of [[WORKFLOW|WORKFLOW]]).
- **AGENTS.md + .agents/skills/** — make the project **standalone**: type, repositories, PR branch and the essentials of the workflow, with **real copies** of the core skills — even someone who doesn't use the PoP can work on the project. **Application** projects embed the **DOX** process there ([[_templates/DOX|template]]): a tree of AGENTS.md files in the code as hierarchical contracts per subtree.
- **memory/** — durable summary of each completed task (final commit + dates); it is the proof that survives after the task's folder in `006_done` is deleted on close (a mandatory step, not periodic cleanup — see [[WORKFLOW|WORKFLOW]]). **worktrees/** — one git worktree per task in execution, always gitignored.
- **skills/** — reusable "how to do X". **specs/** — the detail of each theme.
- **notes/** — notes from the agent **and** the user, with `author: agent | user` frontmatter, in the categories: `learnings/` (lessons from tasks), `decisions/` (decisions extracted from the sheet), `ideas/` (loose ideas) and `references/` (links and external material).

When creating a project, **copy the templates from `_templates/`** and create the empty kanban folders. Don't invent new structures without updating the templates alongside.

## Types and repositories

The PoP is a **repository aggregator**: every project declares a **type** in its AGENTS.md — `default` (a folder in the vault, content at its root, optional repo declared only there), `included` (the project's root is the external repo, with `pop/` committed into it), `multi-repo` (one clone per repo at the folder's root, a single `pop/`) or `full-multi-repo` (several repos, each clone with its own embedded `pop/`; the mother's `pop/` holds the general ROADMAP and a kanban for cross-repo tasks only) — detail in [[TYPES|TYPES]]. Repos of `included`, `multi-repo` and `full-multi-repo` go in the **Aggregated repositories** section of the root [[INDEX|INDEX]]; clones are never committed to the PoP (`.gitignore`).

## IDs and link convention

- IDs follow the hierarchy: epoch `1` → phase `1.1` → task `1.1.1-user-table-creation`. Slug in kebab-case, unique across the vault (if it collides with another project, adjust the slug).
- **Task files move** between kanban stages, so all of them carry the task's unique name in the file name (`1.1.1-user-table-creation.md`, `1.1.1-user-table-creation.plan.md`…) and are linked **by name only**: `[[1.1.1-user-table-creation]]` resolves in any stage.
- **Files that don't move** (sheets, roadmaps, specs, skills, indexes) are linked with full path + alias: `[[categories/agents/my-project/PROJECT|My Project]]`.
- **Links with a trigger:** in agent-facing navigation sections (the card's Links, related specs, memory, learnings, DOX contracts), every link carries 1 line saying **when** to follow it — a link without a trigger there is a link the agent rightly ignores.

## Indexes, INBOX, drafts and open questions

- **`INDEX.md` (root):** vault structure + every project, description of **up to 144 characters** each, and the **Aggregated repositories** list (repos to clone, with path and PR branch).
- **`categories/<category>/INDEX.md`:** per project: link, **status** and description of **up to 600 characters**.
- **`INBOX.md` (root):** everything awaiting the human — generated **automatically via Dataview** from the cards' frontmatter (in `001_initial_task` awaiting your release, `003_human_approval`, critical items in `005_verifying`, blocked ones) and from the open questions in `open_questions/`. Don't edit the lists by hand; it is the only file the human needs to open each day.
- **`drafts/`:** project drafts filled in by the **human** from the templates [[_templates/NEW_PROJECT|NEW_PROJECT]] (→ `drafts/new/`) and [[_templates/IMPORT_PROJECT|IMPORT_PROJECT]] (→ `drafts/import/`) — they let you draft several projects before engaging an agent. The `new-project`/`import-project` skills consume the draft as a pre-answered interview (they confirm, they don't re-ask) and **delete it** when the project is materialized.
- **`open_questions/`:** general questions from the agent that depend on the human and belong to no card — decisions about new projects, overall vault structure etc. One file per question ([[_templates/OPEN-QUESTION|template]], `status: open | answered`); the open ones show up in the INBOX. Answered → the agent applies the answer, marks it `answered` and, if it becomes a harness decision, records it in `notes/decisions/`.

**Project status:** idea | planning | in progress | paused | completed | abandoned

## Core skills of the vault

The central procedures are **skills** in the open Agent Skills format (`SKILL.md`), in `.agents/skills/` — the **only** skills folder in the vault, agent-agnostic. **Never create tool-specific folders** (`.claude/`, `.cursor/` etc.) as a *source* of skills. Agents without native reading of `.agents/skills/` (Claude Code included): read and follow the corresponding `SKILL.md` before performing the operation.

| Skill | When to use |
|-------|-------------|
| `new-project` | Guided interview that creates a new project: essence, harness, roadmap and specs. Consumes a draft from `drafts/new/` if present. |
| `import-project` | Imports an existing repository: recon, fit into type/category and Epoch 1 of organization. Consumes a draft from `drafts/import/` if present. |
| `plan-roadmap` | Build/evolve the roadmap by interview (epochs → phases → candidate tasks). |
| `new-task` | Quick interview that materializes a task in `kanban/001_initial_task`. |
| `advance-task` | Move a task through the 001→006 flow, respecting the human gates. |
| `yolo-critic` | Independent yolo reviewer: judges the brief in 003 and implementation+quality in 005, always in fresh context — Yolo section of [[WORKFLOW\|WORKFLOW]]. |
| `write-spec` | Create/rewrite a standardized spec, with questions per project type. |
| `sync-specs` | Mandatory flow: keep specs faithful to reality as tasks advance. |
| `ingest-research` | Ingests a delivered research result: immutable raw source in `raw/`, synthesis with triggered links and a contradiction check against specs/notes. |
| `weekly-review` | Vault overview: what awaits the human, what is stalled, proposals. |
| `excalidraw-diagram` *(optional, external)* | `.excalidraw` diagrams that argue visually — for specs, plans and notes (pairs with the Obsidian Excalidraw plugin). By [coleam00](https://github.com/coleam00/excalidraw-diagram-skill) — clone it into `.agents/skills/excalidraw-diagram/`. |
| `delegate-coding` | Hub of the coding-skill family: contract for delegating coding work to a headless CLI (always yolo, pre-existing auth with abort on error) and tool choice. Integration into the PoP workflow is a future decision. |
| `run-cursor-agent` | Invoke the headless Cursor CLI (`cursor-agent -p --force`) as the executor of a delegated coding task. |
| `run-opencode` | Invoke headless opencode (`opencode run`) as the executor of a delegated coding task. |
| `run-codex` | Invoke the headless Codex CLI (`codex exec`) as the executor of a delegated coding task. |
| `run-droid` | Invoke Factory's headless droid CLI (`droid exec`) as the executor of a delegated coding task. |
| `clean-code-change` | Clean code practices for whoever writes code: contract before coding, readability, safe refactoring, debt triage — in 002 and 004 of code tasks. **Code projects only.** |
| `clean-code-review` | Code review script with severity (blocking/suggestion/nit) and evidence — in 005 of code tasks and plan/PR gates. **Code projects only.** |
| `frontend-design` | Distinctive visual direction when creating/reshaping UI — typography, aesthetics, escaping the generic AI look. External skill by [anthropics](https://github.com/anthropics/skills), vendored unchanged. Apache 2.0 license. |
| `web-artifacts-builder` | Build elaborate multi-component web artifacts (React, Tailwind, shadcn/ui). External skill by [anthropics](https://github.com/anthropics/skills), vendored unchanged. Apache 2.0 license. |
| `react-best-practices` | React/Next.js performance best practices from Vercel engineering — when writing, reviewing or refactoring. External skill by [vercel-labs](https://github.com/vercel-labs/agent-skills), vendored unchanged. MIT license. |
| `web-design-guidelines` | Review UI code against Web Interface Guidelines (a11y, UX, best practices). External skill by [vercel-labs](https://github.com/vercel-labs/agent-skills), vendored unchanged. MIT license. |
| `taste-skill` | Anti-slop frontend for landing pages, portfolios and redesigns — infers the design direction from the brief. External skill by [Leonxlnx](https://github.com/Leonxlnx/taste-skill), vendored unchanged. MIT license. |
| `impeccable` | Complete design guidance: design, critique, polish and animate interfaces, with commands and anti-pattern detectors. External skill by [pbakaus](https://github.com/pbakaus/impeccable), vendored unchanged. Apache 2.0 license. |
| `skill-a11y-audit` | Accessibility audit (WCAG) with its own scripts. External skill by [snapsynapse](https://github.com/snapsynapse/skill-a11y-audit), vendored unchanged. MIT license. |
| `color-expert` | Color expert: palettes, ramps, gradients, conversions, contrast and perception, with extensive references. External skill by [meodai](https://github.com/meodai/skill.color-expert), vendored unchanged. CC BY 4.0 license. |
| `design-tokens` | Design tokens in the DTCG spec: validation, formats, transformation and color spaces. External skill by [ilikescience](https://github.com/ilikescience/design-tokens-skill), vendored unchanged. MIT license. |
| `shadcn` | Official shadcn/ui skill: add, search, fix and compose shadcn components in projects. External skill by [shadcn-ui](https://github.com/shadcn-ui/ui), vendored unchanged. MIT license. |
| `ux-audit-rethink` | Holistic UX audit (IxDF factors, usability, interaction dimensions) with redesign proposals. External skill by [mastepanoski](https://github.com/mastepanoski/claude-skills), vendored unchanged. MIT license. |
| `nielsen-heuristics-audit` | Evaluate UX/UI against Nielsen's 10 usability heuristics. External skill by [mastepanoski](https://github.com/mastepanoski/claude-skills), vendored unchanged. MIT license. |
| `wcag-accessibility-audit` | WCAG 2.1/2.2 accessibility audit across the 4 POUR principles (A/AA/AAA levels). External skill by [mastepanoski](https://github.com/mastepanoski/claude-skills), vendored unchanged. MIT license. |
| `cognitive-walkthrough` | Deep evaluation of specific tasks simulating novice-user cognition, step by step. External skill by [mastepanoski](https://github.com/mastepanoski/claude-skills), vendored unchanged. MIT license. |
| `ui-design-review` | Visual/aesthetic evaluation: typography, color, spacing, hierarchy, consistency and category conventions. External skill by [mastepanoski](https://github.com/mastepanoski/claude-skills), vendored unchanged. MIT license. |
| `don-norman-principles-audit` | Evaluate UX/UI against Don Norman's 7 design principles. External skill by [mastepanoski](https://github.com/mastepanoski/claude-skills), vendored unchanged. MIT license. |
| `ui-change` | UI design+implementation process: single tone, tokens as a lintable contract, DESIGN.md as memory, 6 mandatory states, anti-drift inventory — in 002 and 004 of frontend tasks. **Frontend projects only.** |
| `ui-review` | UI review with evidence: Nielsen pass/fail with severity 1-4, WCAG 2.2 AA in two layers, screenshot→vision visual loop until severity <2 — in 005 and frontend gates. **Frontend projects only.** |

When creating a new skill: create the folder at `.agents/skills/<name>/SKILL.md` and register it in the table above. When changing a core workflow skill, propagate the copy to the projects' `.agents/skills/` (the `weekly-review` audits the drift; `excalidraw-diagram` is third-party — don't edit it, update it from upstream). The `clean-code-*` skills are copied **only to code projects** — their absence in a writing/work project is not drift.

## Rules for agents working in this vault

1. **Language:** the general content of this vault is written in **English by default — forks may adopt any language**. Each project declares its **default language** in its own AGENTS.md — specs, notes, research, code comments and that project's entire flow follow the declared language (applications also declare the languages supported for i18n).
2. **It is an Obsidian vault:** use wikilinks `[[...]]` for every internal reference, following the link convention above.
3. **Cross-reference within the project:** when mentioning a spec, skill, task or note **from the same project** — or shared vault material (core skills, `_templates/`, [[WORKFLOW|WORKFLOW]], [[TYPES|TYPES]], indexes) — link it following the link convention. Do **not** reference material from **another project** — see rule 4.
4. **Projects are independent islands:** each project is, at first sight, **unrelated** to its neighbors. Never mix material from different projects, and a project **never** references, depends on or integrates another vault project (no "integration epoch", "consumer project" or "sibling project" in the harness). Genuinely cross-project work is exactly what the `multi-repo`/`full-multi-repo` types exist to cover (see [[TYPES|TYPES]]); outside them, only cite another project if the **human explicitly asks**. Every project folder follows the standard anatomy.
5. **Modularization — no file too large:** a note must not exceed **~150 lines** (exception: the AGENTS.md of an **application** project, which embeds the DOX process). A plan is a brief, not an exception: if it grows, split the task or move durable contracts into specs. A file answers **one** question; roadmap descriptions stay one line.
6. **One run = up to the next human gate:** the agent advances the task and only stops where a human decision is awaited — gates and orchestration in [[WORKFLOW|WORKFLOW]].
7. **Explicit owner:** every stage, subtask and skill has a declared owner (`agent` or `user`) and the agent never executes a `(user)` item — table and rules in [[WORKFLOW|WORKFLOW]].
8. **Indexes always in sync:** when creating, completing or changing a project's status, update the category `INDEX.md` **and** the root one. Respect the limits: 144 chars (root), 600 chars (category).
9. **Absolute dates:** always YYYY-MM-DD, never "next week" or "last month".
10. **Decisions are recorded:** important decisions made in conversation go into the project folder (with date and rationale) before ending the session.
11. **Lessons are extracted and integrated:** when completing a task, whatever was learned and is reusable becomes a skill (`skills/`) or a note (`notes/`) — updating an existing note on the same theme instead of duplicating, and flagging contradiction with a previous note/decision — linked in the task's card.
12. **Planning and execution don't mix:** the project's content lives at the **root** of the project folder (or in the external repository indicated in the sheet's harness); all planning and knowledge lives in `pop/`. Legacy projects (pre-2026-07-14): content in `project/` until migration.
13. **Every change to the project goes through the kanban:** agents **never** touch the project content — nothing outside `pop/`, `.agents/` and `AGENTS.md` (in legacy: `project/` and the external repository) — outside a task in `004_processing` with a plan approved in 003 — no "quick fix"; detail in [[WORKFLOW|WORKFLOW]].
14. **Self-validation before finishing:** the agent checks its own changes from the session — index limits (144/600 chars), ~150 lines per note, complete frontmatter on cards, links following the convention — and fixes anything out of bounds before the commit.
15. **Commit per session:** this vault is a git repository. When ending a work session, commit the changes with a short message in the vault's language saying what changed.
16. **Worktrees and ownership:** 004 has one integration worktree per task; parallel fronts use isolated branches/worktrees and only the orchestrator integrates after validating the diff against `owns`. PR in 006 and merge **by the human only** outside yolo; completed `depends_on` are prerequisites — detail in [[WORKFLOW|WORKFLOW]].
17. **Durable memory:** every completed task generates `memory/<id>.md` (≤2000 chars) before deleting the kanban folder — deleting `kanban/006_done/<id>/` is the last mandatory step of 006 (after memory, specs and status), not periodic cleanup; the memory counts as proof; detail in [[WORKFLOW|WORKFLOW]].
18. **Delegation with a floor and ownership:** broad reading leaves the main window and receives a specific question, context/skill, capped sourced output, completion criterion and a “do not do X” boundary. Work below ~5K tokens stays direct except mandatory role separation. Recon arises only from a concrete gap above the floor; **0 workers is normal**. Multi-agent execution uses waves of 3–5 leaf workers and ephemeral contracts with `owns`, `may_read`, `must_not_edit`, `depends_on` and expected input. Parallelism requires logical and write independence; a missing dependency is reported, never implemented opportunistically. The orchestrator validates and integrates.
19. **Work on the vault itself goes to a worktree:** every change to the PoP itself — harness, indexes, project creation/ingestion, decisions, anything **outside** a project's kanban task — is done in its own **git worktree** under `./worktrees/`, with a dedicated branch, so parallel agents don't fight over the working tree, the git index or the branch. The root `worktrees/` folder exists versioned with its contents gitignored (`git worktree add worktrees/<slug>` creates one on demand); when done, integrate the branch into `main` and remove the worktree. Project-task work stays in the **task's** worktree (rule 16), not here.
20. **An explicit human command is sovereign:** the flow's gates and pauses exist to stop the agent from acting in the human's place, not to restrict the human. A direct instruction from them in the conversation overrides any default of the flow — the agent obeys, doesn't reinterpret the request to fit it into the kanban, and records the deviation; facing genuine ambiguity or an irreversible action, it asks **one** question and then executes. Details in [[WORKFLOW|WORKFLOW]].

## Harness decisions

The vault's architecture decisions live in `notes/decisions/`, one note per decision day (`YYYY-MM-DD-harness-decisions.md`) — consult them before proposing harness changes: [[notes/decisions/2026-07-20-harness-decisions|2026-07-20]].

## Open decisions (to discuss)

_None at the moment._
