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
├── TYPES.md             ← project types: uni-repo | multi-repo
├── specs/               ← current contracts, discovered through [[specs/INDEX|the index]]
├── _templates/          ← templates for every standard file
├── notes/               ← vault notes: decisions/ holds the harness decisions
├── researches/          ← the PoP's own deep researches (raw source in raw/, synthesis alongside)
├── scripts/             ← Python CLI (`pop_*`): status, transitions, validation, worktrees and front ownership
├── open_questions/      ← the agent's questions to the human, outside any task ([[_templates/OPEN-QUESTION|template]])
├── drafts/              ← project drafts filled in by the human
│   ├── new/             ← filled-in copies of [[_templates/NEW_PROJECT|NEW_PROJECT]]
│   └── import/          ← filled-in copies of [[_templates/IMPORT_PROJECT|IMPORT_PROJECT]]
└── projects/            ← every project: one folder per project, no category level
    └── <project>/       ← standard anatomy (below)
```

## Anatomy of a project

```
projects/<project>/
├── AGENTS.md            ← standalone instructions: type, repos, workflow (CLAUDE.md → symlink)
├── .agents/skills/      ← real copies of the PoP core workflow skills
├── .gitignore           ← pop/worktrees/ + clones of the project's repos
├── pop/                 ← ALL of the PoP harness, in a single folder
│   ├── PROJECT.md       ← the sheet: what it is, structure, agent harness
│   ├── ROADMAP.md       ← EPOCHS only: one line + status + link each
│   ├── roadmap/         ← 1 file per epoch: phases and tasks, short descriptions
│   ├── MODIFICATIONS.md ← MODIFICATIONS only: one line + status each (created on demand)
│   ├── modifications/   ← 1 file per multi-task modification: tasks, short descriptions
│   ├── researches/      ← research that feeds the roadmap: one folder per topic
│   ├── skills/          ← reusable procedures, one per file
│   ├── specs/           ← specifications, one per theme
│   ├── notes/           ← agent and user notes, by category
│   │   └── learnings/ decisions/ ideas/ references/
│   ├── memory/          ← one folder per date: task ledger + short entries with evidence (005_closing)
│   ├── worktrees/       ← git worktrees of tasks in execution (never committed)
│   └── kanban/          ← flow stages (see [[WORKFLOW|WORKFLOW]])
│       ├── 001_initial_task/ 002_planning/ 003_human_approval/
│       └── 004_processing/ 005_closing/
└── <project content>     ← code, manuscript etc., directly at the root: free structure
```

The dev who opens the project sees only the content, `AGENTS.md`, `.agents/` and `pop/`. **Exception:** projects created **before 2026-07-14** use the legacy anatomy (harness at the folder's root, content in `project/`) until migration — the `pop_*` scripts support both.

- **PROJECT.md** — the sheet: what it is, why it exists, harness. It holds no tasks and no schedule.
- **ROADMAP.md + roadmap/** — the **planned** path, in three levels with descriptions that are always short (≤1 line):
  - **Epoch** (`1`): a big chapter of the project (e.g. "authentication", "payments"). One line in ROADMAP.md, detail in `roadmap/<n>-<slug>.md`.
  - **Phase** (`1.1`): a stage within the epoch (e.g. "user tables", "middleware"). Listed in the epoch's file.
  - **Task** (`1.1.1-<slug>`): the executable unit. It becomes a **folder in the kanban** and travels through the stages described in [[WORKFLOW|WORKFLOW]].
- **MODIFICATIONS.md + modifications/** — the tracking of whatever arrives **outside the plan**: hotfixes, one-off tweaks, contract fixes/changes and small emergent features. Two levels:
  - **Modification** (`M-<n>`): one line in MODIFICATIONS.md; detail in `modifications/m-<n>-<slug>.md` **only when multi-task**. Only the human creates a modification (the agent proposes).
  - **Task** (`M-<n>.<t>-<slug>`): the executable unit, same kanban as the roadmap. A single-task modification lives only in the index line + card.
  - **Before anything, the rule-13 triage:** a pinpoint fix does not even become a modification — it lives only in memory + specs. **Roadmap × modifications frontier (3 questions):** does it fit in ~3 tasks? Does the what/how fit in a card, without a planning interview? Does it only touch existing contracts? Any "no" → roadmap (via `plan-roadmap`). When in doubt, modification — the `weekly-review` proposes promotion to the roadmap when a modification swells (open tasks conclude as `M-`; only the not-yet-tasked work migrates).
  - **The file is a kanban, not a history:** a completed modification's line is **removed** by the `weekly-review` — no log remains; the durable record is memory + specs. `M-<n>` ids are never reused (check memory and the kanban before proposing the next one).
- **Content at the root** — the real work (code, manuscript, repo clones), a fully free structure; if it lives in an external repository, the root holds only the harness and the repo is declared in the project's AGENTS.md. The names `pop` and `project` are **reserved** (don't use them for a content folder or repo). **researches/** — research that grounds the roadmap: one folder per topic, with the immutable raw source in `raw/` and the agent's synthesis alongside (skill `ingest-research`); deep-research prompts proposed by the agent for the **user** to run go in `RESEARCHES.md` (optional, next to the ROADMAP — [[_templates/RESEARCHES|template]]). **Research is always prior:** the agent does not search the web during the task flow — a knowledge gap becomes a prompt in `RESEARCHES.md` (section 002 of [[WORKFLOW|WORKFLOW]]).
- **AGENTS.md + .agents/skills/** — make the project **standalone**: type, repositories, PR branch and the essentials of the workflow, with **real copies** of the core skills — even someone who doesn't use the PoP can work on the project. **Application** projects embed the **DOX** process there ([[_templates/DOX|template]]): a tree of AGENTS.md files in the code as hierarchical contracts per subtree.
- **memory/** — the durable record of every completed task, under `memory/<YYYY-MM-DD>/` (the folder is the completion date): the **ledger** `<id>.md` (≤1200 chars) carries the commit and the dates and is the proof that authorizes removing the task row from the roadmap/modifications and deleting the card folder in `005_closing`; next to it, one **entry** `<id>.<nn>-<slug>.md` (≤800 chars) per thing done, each with a wikilink to the spec or the file that attests the change. Granularity is what lets [[.agents/skills/optimize-memory/SKILL|optimize-memory]] convert and trim file by file, without merging tasks or losing chronology/decisions. **worktrees/** — task worktrees outside a root-local PoP, always gitignored.
- **skills/** — reusable "how to do X". **specs/** — current contracts. A collection becomes canonical atomically when it creates `specs/INDEX.md`: English metadata, `contract|overview`, `draft|active|superseded`, `planned|partial|implemented|not_applicable`, and at most one domain level. See [[specs/spec-architecture|spec architecture]].
- **notes/** — notes from the agent **and** the user, with `author: agent | user` frontmatter, in the categories: `learnings/` (lessons from tasks), `decisions/` (decisions extracted from the sheet), `ideas/` (loose ideas) and `references/` (links and external material).

When creating a project, **copy the templates from `_templates/`** and create the empty kanban folders. Don't invent new structures without updating the templates alongside.

## Types and repositories

The PoP is a **repository aggregator**: every project declares a **type** in its AGENTS.md — `uni-repo` (the folder at `projects/<project>/` **is the repository itself**, with `pop/` committed into it; the **repo-less** variant stays valid, versioned in the PoP) or `multi-repo` (a parent folder **without a harness** aggregating several repos — one clone per repo at the root, each with its own complete `pop/`; **no central kanban**, every task lives in a repo's kanban) — detail in [[TYPES|TYPES]]. The repo of a `uni-repo` (when any) and all the repos of a `multi-repo` go in the **Aggregated repositories** section of the root [[INDEX|INDEX]]; clones are never committed to the PoP (`.gitignore`).

### The root PoP installs and updates the harness

This vault is the **single source** of the harness. Every project that runs standalone — the clone of a `uni-repo`, each repo of a `multi-repo` — never evolves WORKFLOW, templates, scripts or core skills on its own: it receives a **managed copy** via `python3 scripts/pop_install_unirepo.py <dir>`, which mirrors the set declared in [[_templates/unirepo-manifest.json|unirepo-manifest]]. Each install writes into the target's `pop/.unirepo-harness.json` both the source harness's `content_sha` and the **inventory** of what it wrote: the stamp makes "up to date" verifiable (`--check-fresh <dir>` fails closed when the target fell behind, and `pop_validate` reports staleness as a violation), and the inventory authorizes the next update's pruning — only what the installer brought before may be removed, because **a managed folder is not an exclusive folder** and the project keeps files of its own in `pop/scripts/`. Only the source **compares** versions; run from the installed copy, `--check-fresh` reports just the local version, because sending the project to look for the source is teaching it to cross its own boundary. Fixing harness by editing the local copy is always wrong — the project **reinstalls**.

**What travels is scope-relative.** Every managed file describes exclusively the root that receives it: whoever installs it never appears in it. `exclude_files` drops from the package what only serves a host of projects (`TYPES.md`, `NEW_PROJECT`/`IMPORT_PROJECT`, the `weekly-review` origin fronts), and `pop_install_unirepo.py --audit-boundary` **fails the install** if the copied text goes back to naming this vault — `projects/`, root indexes, "meta-project", "parent PoP". The scripts follow the same rule: `poplib.vault_root()` stops at the `pop/.unirepo-harness.json` marker, and an installed scope labels itself by the name of its own root, never `pop` (which would make it inherit delivery straight to `main`). The operational definition lives in the "Current scope" section of [[WORKFLOW|WORKFLOW]], which ships with every copy — *read it before touching anything that goes out to the projects*.

## IDs and link convention

- IDs follow the hierarchy of their origin: roadmap epoch `1` → phase `1.1` → task `1.1.1-user-table-creation`; modifications modification `M-1` → task `M-1.1-adjust-contract`. Numeric id = roadmap; `M-` prefix = modifications. Slug in kebab-case, unique across the vault (if it collides with another project, adjust the slug).
- **Task files move** between kanban stages, so all of them carry the task's unique name in the file name (`1.1.1-user-table-creation.md`, `M-1.1-adjust-contract.plan.md`…) and are linked **by name only**: `[[1.1.1-user-table-creation]]` resolves in any stage.
- **Files that don't move** (sheets, roadmaps, modifications, specs, skills, indexes) are linked with full path + alias: `[[projects/my-project/PROJECT|My Project]]`.
- **Links with a trigger:** in agent-facing navigation sections (the card's Links, related specs, memory, learnings, DOX contracts), every link carries 1 line saying **when** to follow it — a link without a trigger there is a link the agent rightly ignores.

## Indexes, INBOX, drafts and open questions

- **`INDEX.md` (root):** vault structure + every project — link, **status** and description of **up to 144 characters** each — and the **Aggregated repositories** list (repos to clone, with path and PR branch). There is no intermediate per-category index anymore: the root INDEX is the vault's only project index.
- **`INBOX.md` (root):** everything awaiting the human — generated **automatically via Dataview** from the cards' frontmatter (in `001_initial_task` awaiting your release, `003_human_approval`, awaiting merge in `005_closing`, blocked ones) and from the open questions in `open_questions/`. Don't edit the lists by hand; it is the only file the human needs to open each day.
- **`drafts/`:** project drafts filled in by the **human** from the templates [[_templates/NEW_PROJECT|NEW_PROJECT]] (→ `drafts/new/`) and [[_templates/IMPORT_PROJECT|IMPORT_PROJECT]] (→ `drafts/import/`) — they let you draft several projects before engaging an agent. The `new-project`/`import-project` skills consume the draft as a pre-answered interview (they confirm, they don't re-ask) and **delete it** when the project is materialized.
- **`open_questions/`:** general questions from the agent that depend on the human and belong to no card — decisions about new projects, overall vault structure etc. One file per question ([[_templates/OPEN-QUESTION|template]], `status: open | answered`); the open ones show up in the INBOX. Answered → the agent applies the answer, marks it `answered` and, if it becomes a harness decision, records it in `notes/decisions/`.

**Project status:** idea | planning | in progress | paused | completed | abandoned

## Core skills of the vault

The central procedures are **skills** in the open Agent Skills format (`SKILL.md`), in `.agents/skills/` — the **only** skills folder in the vault, agent-agnostic. **Never create tool-specific folders** (`.claude/`, `.cursor/` etc.) as a *source* of skills. Agents without native reading of `.agents/skills/` (Claude Code included): read and follow the corresponding `SKILL.md` before performing the operation.

| Skill | When to use |
|-------|-------------|
| `new-project` | Guided interview that creates a new project: essence, harness, roadmap and specs. Consumes a draft from `drafts/new/` if present. |
| `import-project` | Imports an existing repository: recon, fit into type and Epoch 1 of organization. Consumes a draft from `drafts/import/` if present. |
| `recon-project` | Generates and consumes the deterministic `RECON.md` report of a directory before sweeping files — delegated recon, 002 with broad reading, Epoch 1 of `import-project`. |
| `plan-roadmap` | Build/evolve the roadmap by interview (epochs → phases → candidate tasks). |
| `new-task` | Quick interview that materializes a roadmap or modification task in `kanban/001_initial_task`; also handles change requests with no active card. |
| `advance-task` | Move a task through the 001→005_closing flow, respecting the human gates. |
| `judge-dredd` | Judge Dredd, yolo's single judge with a fixed native profile: `005_closing` for every yolo task and 003 only for `critical`; judges by reading, decides route/delta, directed repair and circuit breaker — [[WORKFLOW\|WORKFLOW]]. |
| `create-agent-generic` | Maintain the six agent-agnostic specialist contracts and guide runtime translations without introducing tool-specific semantics. |
| `create-agent-claude-code` | Generate and validate the six Claude Code specialists with explicit profiles and transactional writes. |
| `create-agent-codex` | Generate and locally validate six standalone Codex custom-agent TOMLs with fixed model and effort. |
| `create-agent-kimi-code` | Generate and validate six Kimi Code agents with symbolic `primary\|secondary` routing and K2.7 secondary. |
| `create-agent-opencode` | Generate and validate six OpenCode subagents with closed provider/model IDs, permissions, and nesting. |
| `write-spec` | Create/rewrite a standardized spec, with questions per project type. |
| `sync-specs` | Mandatory flow: keep specs faithful to reality as tasks advance. |
| `ingest-research` | Ingests a delivered research result: immutable raw source in `raw/`, synthesis with triggered links and a contradiction check against specs/notes. |
| `weekly-review` | Review of the current scope **outside the kanban**, in parallel waves: it measures, **fixes the harness** wherever the call is unambiguous, and proposes the rest. The fronts for whoever hosts projects live in `origin-scope.md`, which is not installed. |
| `optimize-memory` | Convert legacy memory into date folder + ledger + entries, and trim whatever exceeds the cap — **outside the kanban**, in parallel waves per file, without merging tasks or losing chronology, commits/PRs or critical decisions. |
| `excalidraw-diagram` *(optional, external)* | `.excalidraw` diagrams that argue visually — for specs, plans and notes (pairs with the Obsidian Excalidraw plugin). By [coleam00](https://github.com/coleam00/excalidraw-diagram-skill) — clone it into `.agents/skills/excalidraw-diagram/`. |
| `coding-sandbox` | Only by explicit request: inspect, propose, and, after exact confirmation, create an interactive local coding docker; never replaces `delegate-coding`. |
| `delegate-coding` | Hub of the coding-skill family: contract for delegating coding work to a headless CLI (always yolo, pre-existing auth with abort on error) and tool choice. Integration into the PoP workflow is a future decision. |
| `run-cursor-agent` | Invoke the headless Cursor CLI (`cursor-agent -p --force`) as the executor of a delegated coding task. |
| `run-opencode` | Invoke headless opencode (`opencode run`) as the executor of a delegated coding task. |
| `run-codex` | Invoke the headless Codex CLI (`codex exec`) as the executor of a delegated coding task. |
| `run-droid` | Invoke Factory's headless droid CLI (`droid exec`) as the executor of a delegated coding task. |
| `charm-bubbletea` | Elm framework for Go TUIs (Model/Update/View, Cmd/Msg) — the base of every vault TUI. **Go TUI projects only.** |
| `charm-huh` | Terminal forms and prompts in Go (Form/Group/Field, validation, themes) to collect user input. **Go TUI projects only.** |
| `charm-glamour` | Markdown rendering in the terminal (TermRenderer, styles, word wrap) — core of the PoP markdown reading/editing tools. **Go TUI projects only.** |
| `charm-bubbles` | Ready-made Go TUI components (list, viewport, spinner, table, textinput…) as embeddable `tea.Model`s. **Go TUI projects only.** |
| `charm-lipgloss` | Terminal style and layout in Go (immutable Style, adaptive colors, Join/Place, tables). **Go TUI projects only.** |
| `clean-code-change` | Clean code practices for whoever writes code: contract before coding, readability, safe refactoring, debt triage — in 002 and 004 of code tasks. **Code projects only.** |
| `clean-code-review` | Code review script with severity (blocking/suggestion/nit) and evidence — in `005_closing` of code tasks and plan/PR gates. **Code projects only.** |
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
| `ui-review` | UI review with evidence: Nielsen pass/fail with severity 1-4, WCAG 2.2 AA in two layers, screenshot→vision visual loop until severity <2 — in `005_closing` and frontend gates. **Frontend projects only.** |

When creating a new skill: create the folder at `.agents/skills/<name>/SKILL.md` and register it in the table above. When changing a core workflow skill, propagate the copy to the projects' `.agents/skills/` (the `weekly-review` audits the drift; `excalidraw-diagram` is third-party — don't edit it, update it from upstream). The `clean-code-*` skills are copied **only to code projects** — their absence in a writing/work project is not drift.

## Rules for agents working in this vault

1. **Language:** the general content of this vault is written in **English by default — forks may adopt any language**. Each project declares its **default language** in its own AGENTS.md — specs, notes, research, code comments and that project's entire flow follow the declared language (applications also declare the languages supported for i18n).
2. **It is an Obsidian vault:** use wikilinks `[[...]]` for every internal reference, following the link convention above.
3. **Cross-reference within the project:** when mentioning a spec, skill, task or note **from the same project** — or shared vault material (core skills, `_templates/`, [[WORKFLOW|WORKFLOW]], [[TYPES|TYPES]], indexes) — link it following the link convention. Do **not** reference material from **another project** — see rule 4.
4. **Projects are independent islands:** each project is, at first sight, **unrelated** to its neighbors. Never mix material from different projects, and a project **never** references, depends on or integrates another vault project (no "integration epoch", "consumer project" or "sibling project" in the harness). Genuinely cross-project work is exactly what the `multi-repo` type exists to cover (see [[TYPES|TYPES]]); outside it, only cite another project if the **human explicitly asks**. Every project folder follows the standard anatomy.
5. **Modularization — no file too large:** a note must not exceed **~150 lines**; a project's AGENTS.md is capped at **~60** and the ruler **always measures**: in an **application**, `pop_validate` discounts the DOX block and reports the rest's excess as a warning — an exemption that switches the measurement off is invisible debt, not an exception. A project AGENTS.md holds what belongs to that project and **points** to [[WORKFLOW|WORKFLOW]]/[[TYPES|TYPES]] — narrating the flow there is duplication that rots ([[_templates/AGENTS-PROJECT|the template]] lists what must not go in). A plan is a brief, not an exception: if it grows, split the task or move durable contracts into specs. A file answers **one** question; roadmap descriptions stay one line.
6. **One run = up to the next human gate:** the agent advances the task and only stops where a human decision is awaited — gates and orchestration in [[WORKFLOW|WORKFLOW]].
7. **Explicit owner:** every stage, subtask and skill has a declared owner (`agent` or `user`) and the agent never executes a `(user)` item — table and rules in [[WORKFLOW|WORKFLOW]].
8. **Index always in sync:** when creating, completing or changing a project's status, update the root `INDEX.md`. Respect the limit: 144 chars per description.
9. **Absolute dates:** always YYYY-MM-DD, never "next week" or "last month".
10. **Decisions are recorded:** important decisions made in conversation go into the project folder (with date and rationale) before ending the session.
11. **Lessons are extracted and integrated:** when completing a task, whatever was learned and is reusable becomes a skill (`skills/`) or a note (`notes/`) — updating an existing note on the same theme instead of duplicating, and flagging contradiction with a previous note/decision — linked in the task's card.
12. **Planning and execution don't mix:** the project's content lives at the **root** of the project folder (or in the external repository indicated in the sheet's harness); all planning and knowledge lives in `pop/`. Legacy projects (pre-2026-07-14): content in `project/` until migration.
13. **A content change enters through triage — optional kanban, tracking always:** every content change request is classified at the entrance. **Direct fix** when *all* hold: the scope is evident from the request itself, no new durable contract, no planning interview needed, and it fits in one session — it runs **without a card**, with durable proof in a memory ledger `F-YYYYMMDD-<slug>` + sync of the affected specs ("Direct fix" section of [[WORKFLOW|WORKFLOW]]); a fix is not a waiver: memory and specs stay mandatory. Outside the direct fix, the kanban is **optional and recommended by the agent when the change is large**; if the user opts out of it, the route is **the coding agent's own plan mode**, with no card and no stages — but **never** without tracking: a `D-YYYYMMDD-<slug>` ledger + entries + specs/DOX sync, and the project's agents and skills keep applying ("No-kanban route" section of [[WORKFLOW|WORKFLOW]]). **Yolo or a roadmap/modifications item → kanban by default**, implied: the agent warns ("this goes through the kanban") and proceeds; when in doubt, **one** one-line question decides. A fix that grows midway (second objective, contract touched) **stops** and returns to triage. Harness stays outside the kanban as always: **harness maintenance is done directly, with no card, no task branch/worktree/PR** (the three classes of file are in the "Current scope" section of [[WORKFLOW|WORKFLOW]]); creating a task to slim an AGENTS.md, fix a spec, a note or memory is a routing error, not diligence.
14. **Self-validation before finishing:** the agent checks its own changes from the session — the index limit (144 chars), ~150 lines per note, complete frontmatter on cards, links following the convention — and fixes anything out of bounds before the commit.
15. **Commit per session:** this vault is a git repository. When ending a work session, commit the changes with a short message in the vault's language saying what changed.
16. **Worktrees and ownership:** outside a root-local PoP, 004 has one integration worktree per task. External yolo tasks integrate into `develop`; the final scope opens `develop` → `main`, and only the human merges. Dependencies are prerequisites — [[WORKFLOW|WORKFLOW]].
17. **Durable memory and lean roadmap:** every completed task gets its ledger `memory/<YYYY-MM-DD>/<id>.md` (≤1200 chars) plus one entry `<id>.<nn>-<slug>.md` (≤800 chars, with linked evidence) per thing done. After memory/spec/status validation, the close-out of `005_closing` removes its row from the epoch or modification file and only then deletes `kanban/005_closing/<id>/`. Root roadmaps hold epochs; epoch files hold phases and open tasks; `MODIFICATIONS.md` and `modifications/` follow the same rule.
18. **Main agent is delegation-first, with a floor and ownership:** there is no `pop-orchestrator` custom agent. The native main session reads this `AGENTS.md`, retains routing, gates, transitions, and integration, and **always delegates** planning, recon, execution, judgment, and phase verification to the six specialists in [[specs/multi-agent-orchestration|the multi-agent contract]]. It works directly only on genuinely small, simple actions below the delegation floor with no mandatory context separation. Every call carries only an authorization envelope: role/route, paths, `may_read`, `owns`, `must_not_edit`, web/skills, dependencies/expected input, gate/delta, and required output with format/cap/evidence/status. The specialist acquires substantive context at the source; the main agent never replays it. Reading below ~5K tokens may stay direct; recon exists only for a concrete gap above the floor, and zero recon workers is normal. A cohesive front receives `pop-executor`; a DAG, multiple skills, or multiple write sets receive `pop-execution-orchestrator`. Parallelism requires logical and write independence. Missing/incompatible input returns `BLOCKED`; only the main agent validates and integrates.
19. **Root-local PoP delivery:** when the scope is this vault root and the card declares `project: pop`, execute and close directly on `main`, without a task branch/worktree/PR. Improving the PoP **as the tool this vault distributes** — WORKFLOW/TYPES, a new skill, `scripts/` — is meta-project content and still requires a task in the root kanban. That does **not propagate into a project**: a project's harness is not its product, and touching it follows rule 13 (directly, with no card). External projects and repositories follow rule 16 and are never changed by a root-PoP task.
20. **An explicit human command is sovereign, with no implicit waiver:** the gates stop the agent from acting in the human's place; they do not restrict the human. A direct instruction overrides **only** the rule or gate it names; the agent obeys within that scope and records the deviation. **Opting out of the kanban is not a deviation** — it is a legitimate triage choice (rule 13) that waives the stages but never continuity: identifiable memory (`D-`) and a recorded specs/DOX impact assessment stay mandatory. Genuine ambiguity or an irreversible action allows **one** question. Details in [[WORKFLOW|WORKFLOW]].

## Harness decisions

The vault's architecture decisions live in `notes/decisions/`, one note per decision day (`YYYY-MM-DD-harness-decisions.md`) — consult them before proposing harness changes: [[notes/decisions/2026-07-20-harness-decisions|2026-07-20]] · [[notes/decisions/2026-07-22-harness-decisions|2026-07-22]] · [[notes/decisions/2026-08-16-harness-decisions|2026-08-16]] · [[notes/decisions/2026-08-18-harness-decisions|2026-08-18]].

## Open decisions (to discuss)

_None at the moment._
