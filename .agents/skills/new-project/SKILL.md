---
name: new-project
description: Guided interview that creates a new project in the vault - essence, harness, roadmap and initial specs, step by step with the user. Use when the user asks to create/register a new project.
---

# new-project

Creates a new project in `projects/<project>/` **by interviewing the user in steps** — no creating the structure with placeholders and walking away. Anatomy: the "Anatomy of a project" section of [[AGENTS|AGENTS]]; variations per type: [[TYPES|TYPES]].

**Delegate to subagents:** almost nothing — the interview is with the user; step 4's epoch recon delegates via `plan-roadmap`.

## How to conduct

- One step at a time, 2–4 questions per block. Reflect back what you understood before moving on.
- "I don't know yet" is a valid answer → record it as an open question (in the project sheet or in a draft spec), don't block creation.
- If the user already answered something spontaneously, don't ask again — confirm.
- **Draft in `drafts/new/`?** Use it as a pre-answered interview ([[_templates/NEW_PROJECT|template]]): confirm what is filled in instead of asking; an empty field or "I don't know" follows the steps normally. An open question that **blocks** a human decision → file in `open_questions/` ([[_templates/OPEN-QUESTION|template]]). When materializing the project, **delete the draft** — its content now lives in the project.

## Step 1 — Essence

Ask: **(a)** what is the project, in one or two sentences? **(b)** what does success look like — how will you know it worked? **(c)** what kind is it (programming, writing, business, research, personal...)? At the end, propose a kebab-case name and confirm — the name becomes the folder in `projects/<name>/`, with no category level.

## Step 2 — Type and repositories

Ask: **(a)** what is the **type** — `uni-repo` | `multi-repo` (explain using [[TYPES|TYPES]])? **(b)** are there repository(ies)? URL(s) and name of each — optional (one) if `uni-repo`; **listing all of them is mandatory** if `multi-repo`. **(c)** what is the **PR branch** — where task worktrees open PRs to (e.g. `main`)?

## Step 3 — Context and harness

Ask: **(a)** tools and constraints agents must respect? **(b)** tone/style, if applicable? **(c)** are this project's tasks critical by default (extra human gate on verification)? **(d)** does any project in the vault relate to this one? **(e)** what is the **project's default language** — specs, notes, research, code comments and the whole flow follow that language (declared in the project's AGENTS.md)? **(f)** if it is an application: which **languages must the application support** (i18n) — also in the AGENTS.md, so the roadmap and specs handle it from the start?

## Step 4 — Roadmap

Follow the **`plan-roadmap`** skill: destination → epoch brainstorm (you propose, the user reacts) → cut → phases for the first epoch only → candidate tasks. Topics that require external knowledge the agent can't reach on its own → offer to create the **`RESEARCHES.md`** (optional, `_templates/RESEARCHES.md`): deep-research prompts for the user to run and deposit in `pop/researches/`.

## Step 5 — Initial specs

From the topics that surfaced in the previous steps, propose which deserve a spec right away. For each one accepted, follow the **`write-spec`** skill (they may be born as `draft` with a full "Open" section — that's expected).

## Step 6 — Materialization

1. Create the standard anatomy and real copies of the workflow skills, including `judge-dredd` and `optimize-memory`. Create canonical `pop/specs/INDEX.md` whenever initial specs are accepted, migrating that collection atomically. Use the project's declared language and leave no placeholders.
2. **Type `uni-repo` with a repo:** the project folder **is the repo clone itself** (`projects/<project>/`); run `python3 scripts/pop_install_unirepo.py <repo>` to install or update the standalone `pop/` committed in the repo (with WORKFLOW.md, TYPES.md, INBOX.md, `_templates/` and `scripts/` inside `pop/`), with `AGENTS.md` and `.agents/skills/` at the clone's root; add the clone's path to the PoP **root** `.gitignore`. **No repo:** the `projects/<project>/` folder is the project root itself, versioned in the PoP — content and harness live together in it. Never create tool-specific folders (`.claude/` etc.) — the vault is agent-agnostic.
3. **Type `multi-repo`:** the parent folder at `projects/<project>/` stays **harness-free** — only `AGENTS.md`, `INDEX.md` (referencing the repos) and a general `ROADMAP.md`, reserved for cross-repo plans; **no `pop/`, no central kanban** (tasks, specs and memory live in the repos). Each repo, cloned at the root of the parent folder (`projects/<project>/<repo>/`), is installed as a `uni-repo` via `python3 scripts/pop_install_unirepo.py <repo>`, with `pop/worktrees/` in the **repo's** `.gitignore`. Each repo's AGENTS.md declares `type: uni-repo` + a **"Part of"** section linking the parent and the general ROADMAP, without preventing standalone use. The **parent's** `.gitignore` ignores the clones; each repo gets its own ROADMAP (in its `pop/`) and the general ROADMAP points to them with a trigger.
4. **Application (programming):** paste into the project's AGENTS.md the full section from `_templates/DOX.md` (it may exceed ~150 lines to accommodate it) — the code's context follows the DOX process: a tree of AGENTS.md as per-subtree contracts, started when the code is born.
5. **Register the repositories and the index in the same session:** a `uni-repo` with a repo → the repo; a `multi-repo` → all repos — in the **Aggregated repositories** table of the root `INDEX.md`; the project's entry in the root `INDEX.md` (link, ≤144 chars).
6. No `<...>` placeholder may remain; dates in YYYY-MM-DD. Close with a summary: what was created, open questions and a suggestion for the first task (`new-task` skill).

## Cautions

- **Project that already exists** (repository or folder with content) → use the `import-project` skill, not this one: there reality comes first and Epoch 1 is organization.
- Wikilinks for fixed files: full path + alias (`[[projects/my-project/PROJECT|My Project]]`).
- Don't create tasks here — that's the `new-task` skill.
