---
name: new-project
description: Guided interview that creates a new project in the vault - essence, harness, roadmap and initial specs, step by step with the user. Use when the user asks to create/register a new project.
---

# new-project

Creates a new project in `<category>/<project>/` **by interviewing the user in steps** — no creating the structure with placeholders and walking away. The standard anatomy is in AGENTS.md (root).

## How to conduct

- One step at a time, 2–4 questions per block. Reflect back what you understood before moving on.
- "I don't know yet" is a valid answer → record it as an open question (in the project sheet or in a draft spec), don't block creation.
- If the user already answered something spontaneously, don't ask again — confirm.

## Step 1 — Essence

Ask: **(a)** what is the project, in one or two sentences? **(b)** what does success look like — how will you know it worked? **(c)** what kind is it (programming, writing, business, research, personal...)? **(d)** which vault category does it belong to (`agents` | `applications` | `writing` | `work` — or propose a new one, confirming)?

Propose a kebab-case name and confirm.

## Step 2 — Type and repositories

Ask: **(a)** what is the **type** (explain using the root TYPES.md): `default` — work in `project/`, harness in the PoP; `included` — PoP harness inside the project's own repo; `multi-repo` — several repositories in `project/`? **(b)** are there repository(ies)? URL(s) and name of each — **listing all of them is mandatory** if `multi-repo`. **(c)** what is the **PR branch** — where task worktrees open PRs to (e.g. `main`)?

## Step 3 — Context and harness

Ask: **(a)** tools and constraints agents must respect? **(b)** tone/style, if applicable? **(c)** are this project's tasks critical by default (extra human gate on verification)? **(d)** does any project in the vault relate to this one? **(e)** what is the **project's default language** — specs, notes, research, code comments and the whole flow follow that language (declared in the project's AGENTS.md)? **(f)** if it is an application: which **languages must the application support** (i18n) — also in the AGENTS.md, so the roadmap and specs handle it from the start?

## Step 4 — Roadmap

Follow the **`plan-roadmap`** skill: destination → epoch brainstorm (you propose, the user reacts) → cut → phases for the first epoch only → candidate tasks. Topics that require external knowledge the agent can't reach on its own → offer to create the **`RESEARCHES.md`** (optional, `_templates/RESEARCHES.md`): deep-research prompts for the user to run and deposit in `researches/`.

## Step 5 — Initial specs

From the topics that surfaced in the previous steps, propose which deserve a spec right away. For each one accepted, follow the **`write-spec`** skill (they may be born as `draft` with a full "Open" section — that's expected).

## Step 6 — Materialization

1. Create the structure (variations per type: TYPES.md at the root):
   ```
   <category>/<project>/
   ├── AGENTS.md       ← _templates/AGENTS-PROJECT.md (type, repos, PR branch, language, i18n) + symlink CLAUDE.md → AGENTS.md
   ├── .agents/skills/ ← real copies of the root core skills: new-task, advance-task, plan-roadmap, write-spec, sync-specs
   ├── .gitignore      ← worktrees/ + paths of the project's clones
   ├── PROJECT.md      ← _templates/PROJECT.md filled with steps 1–3
   ├── ROADMAP.md      ← _templates/ROADMAP.md filled with step 4
   ├── RESEARCHES.md   ← optional: deep-research prompts for the user (_templates/RESEARCHES.md)
   ├── roadmap/  project/  researches/  skills/  specs/  memory/  worktrees/
   ├── notes/learnings  notes/decisions  notes/ideas  notes/references
   └── kanban/001_initial_task … kanban/006_done  (6 empty folders)
   ```
   `project/` according to the type: `default` — the real work (gitignored repo clone, if any); `included` — doesn't exist; `multi-repo` — one subdirectory per repo. `researches/`: one folder per topic.
2. **Type `included` with a repo:** clone the repo into `<category>/<project>/` and build the anatomy **inside it**, with the core skill copies in `.agents/skills/` and `_templates/`, `WORKFLOW.md` and `TYPES.md` copied from the root; add the clone's path to the PoP **root** `.gitignore`. Never create tool-specific folders (`.claude/` etc.) — the vault is agent-agnostic.
3. **Application (programming):** paste into the project's AGENTS.md the full section from `_templates/DOX.md` (it may exceed ~150 lines to accommodate it) — the code's context follows the DOX process: a tree of AGENTS.md as per-subtree contracts, started when the code is born. Type `default` with a repo that must stay clean of AI files → ask whether the tree is committed (default) or only the root contract stays in the PoP.
4. **Register the repositories:** `included`/`multi-repo` → **Aggregated repositories** table in the root `INDEX.md`; `default` → only in the project's AGENTS.md.
5. Update the indexes in the same session: `<category>/INDEX.md` (link, status, ≤600 chars) and root `INDEX.md` (link, ≤144 chars).
6. No `<...>` placeholder may remain; dates in YYYY-MM-DD.
7. Close with a summary: what was created, questions left open and a suggestion for the first task (`new-task` skill).

## Cautions

- **Project that already exists** (repository or folder with content) → use the `import-project` skill, not this one: there reality comes first and Epoch 1 is organization.
- Wikilinks for fixed files: full path + alias (`[[agents/my-project/PROJECT|My Project]]`).
- Don't create tasks here — that's the `new-task` skill.
