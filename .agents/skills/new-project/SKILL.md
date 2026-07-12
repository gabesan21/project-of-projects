---
name: new-project
description: Guided interview that creates a new project in the vault - essence, harness, roadmap and initial specs, step by step with the user. Use when the user asks to create/register a new project.
---

# new-project

Creates a new project in `categories/<category>/<project>/` **by interviewing the user in steps** — no creating the structure with placeholders and walking away. Anatomy: the "Anatomy of a project" section of [[AGENTS|AGENTS]]; variations per type: [[TYPES|TYPES]].

**Delegate to subagents:** almost nothing — the interview is with the user; step 4's epoch recon delegates via `plan-roadmap`.

## How to conduct

- One step at a time, 2–4 questions per block. Reflect back what you understood before moving on.
- "I don't know yet" is a valid answer → record it as an open question (in the project sheet or in a draft spec), don't block creation.
- If the user already answered something spontaneously, don't ask again — confirm.
- **Draft in `drafts/new/`?** Use it as a pre-answered interview ([[_templates/NEW_PROJECT|template]]): confirm what is filled in instead of asking; an empty field or "I don't know" follows the steps normally. An open question that **blocks** a human decision → file in `open_questions/` ([[_templates/OPEN-QUESTION|template]]). When materializing the project, **delete the draft** — its content now lives in the project.

## Step 1 — Essence

Ask: **(a)** what is the project, in one or two sentences? **(b)** what does success look like — how will you know it worked? **(c)** what kind is it (programming, writing, business, research, personal...)? **(d)** which vault category does it belong to (in `categories/`: `agents` | `applications` | `writing` | `work` — or propose a new one, confirming)? At the end, propose a kebab-case name and confirm.

## Step 2 — Type and repositories

Ask: **(a)** what is the **type** — `default` | `included` | `multi-repo` | `full-multi-repo` (explain using [[TYPES|TYPES]])? **(b)** are there repository(ies)? URL(s) and name of each — **listing all of them is mandatory** if `multi-repo`/`full-multi-repo`. **(c)** what is the **PR branch** — where task worktrees open PRs to (e.g. `main`)?

## Step 3 — Context and harness

Ask: **(a)** tools and constraints agents must respect? **(b)** tone/style, if applicable? **(c)** are this project's tasks critical by default (extra human gate on verification)? **(d)** does any project in the vault relate to this one? **(e)** what is the **project's default language** — specs, notes, research, code comments and the whole flow follow that language (declared in the project's AGENTS.md)? **(f)** if it is an application: which **languages must the application support** (i18n) — also in the AGENTS.md, so the roadmap and specs handle it from the start?

## Step 4 — Roadmap

Follow the **`plan-roadmap`** skill: destination → epoch brainstorm (you propose, the user reacts) → cut → phases for the first epoch only → candidate tasks. Topics that require external knowledge the agent can't reach on its own → offer to create the **`RESEARCHES.md`** (optional, `_templates/RESEARCHES.md`): deep-research prompts for the user to run and deposit in `researches/`.

## Step 5 — Initial specs

From the topics that surfaced in the previous steps, propose which deserve a spec right away. For each one accepted, follow the **`write-spec`** skill (they may be born as `draft` with a full "Open" section — that's expected).

## Step 6 — Materialization

1. Create the structure — anatomy: the "Anatomy of a project" section of [[AGENTS|AGENTS]]; variations per type: [[TYPES|TYPES]]. This skill's specifics: the project's AGENTS.md from `_templates/AGENTS-PROJECT.md` (type, repos, PR branch, language, i18n) + CLAUDE.md symlink; real copies of the root core skills in `.agents/skills/` (new-task, advance-task, plan-roadmap, write-spec, sync-specs); PROJECT.md/ROADMAP.md from the templates, filled with steps 1–4; optional RESEARCHES.md (`_templates/RESEARCHES.md`); the 6 empty kanban folders.
2. **Type `included` with a repo:** clone the repo into `categories/<category>/<project>/` and build the anatomy **inside it**, with the core skill copies in `.agents/skills/` and `_templates/`, `WORKFLOW.md` and `TYPES.md` copied from the root; add the clone's path to the PoP **root** `.gitignore`. Never create tool-specific folders (`.claude/` etc.) — the vault is agent-agnostic.
3. **Type `full-multi-repo`:** the main folder in the PoP stays **reduced** — no `specs/` and no `memory/`, kanban **for cross-repo tasks only** — and each repo is cloned into `project/<repo>/` receiving **inside it** the full `included` installation from item 2 (anatomy, core skills, `_templates/`, `WORKFLOW.md`, `TYPES.md`), with `worktrees/` in the **repo's** `.gitignore`. Each repo's AGENTS.md declares `type: included` + a **"Part of"** section linking the parent project, the general ROADMAP and the cross kanban. The **project's** `.gitignore` ignores `worktrees/` and the clones; each repo gets its own ROADMAP and the general ROADMAP points to them with a trigger.
4. **Application (programming):** paste into the project's AGENTS.md the full section from `_templates/DOX.md` (it may exceed ~150 lines to accommodate it) — the code's context follows the DOX process: a tree of AGENTS.md as per-subtree contracts, started when the code is born. Type `default` with a repo that must stay clean of AI files → ask whether the tree is committed (default) or only the root contract stays in the PoP.
5. **Register the repositories and indexes in the same session:** `included`/`multi-repo`/`full-multi-repo` → **Aggregated repositories** table in the root `INDEX.md` (`default` → only in the project's AGENTS.md); `categories/<category>/INDEX.md` (link, status, ≤600 chars) and root `INDEX.md` (link, ≤144 chars).
6. No `<...>` placeholder may remain; dates in YYYY-MM-DD. Close with a summary: what was created, open questions and a suggestion for the first task (`new-task` skill).

## Cautions

- **Project that already exists** (repository or folder with content) → use the `import-project` skill, not this one: there reality comes first and Epoch 1 is organization.
- Wikilinks for fixed files: full path + alias (`[[categories/agents/my-project/PROJECT|My Project]]`).
- Don't create tasks here — that's the `new-task` skill.
