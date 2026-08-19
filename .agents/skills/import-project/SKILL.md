---
name: import-project
description: Imports an existing repository or project into the vault - codebase recon, fit interview (type, language) and a mandatory Epoch 1 of organization (faithful specs, skills, research, notes), with a gate that blocks changes to the project until it completes. Use when the user asks to import/add an existing project or repository to the PoP.
---

# import-project

Brings a project **that already exists** (repository or local folder) into the PoP. Unlike `new-project`, here reality comes first: the agent does **recon of the codebase before asking**, and the roadmap is born **from where the project stands** — **Epoch 1 is always "Organization"**: building specs, skills, research and notes faithful to what exists. Until it completes, **no change to the project is accepted**.

**Delegate to subagents:** the entire recon of Step 1 (parallel subagents, one per front, each answer ≤30 lines); the interview and materialization stay with the main agent.

## How to conduct

- Recon first, read-only; then interview in blocks of 2–4 questions, reflecting back what you understood.
- "I don't know" is a valid answer → it becomes RECON NEEDED (with the check that resolves it) or an "Open" item in a spec.
- If the recon already answered something, don't ask — **confirm** ("I saw X in the code; is that right?").
- **Draft in `drafts/import/`?** Use it as a pre-answered interview ([[_templates/IMPORT_PROJECT|template]]): confirm what is filled in instead of asking; a divergence between draft and recon → RECON NEEDED. An open question that **blocks** a human decision → file in `open_questions/` ([[_templates/OPEN-QUESTION|template]]). When materializing the project, **delete the draft**.

## Step 1 — Codebase recon

1. Ask where the project lives: repository URL and/or local path. Clone/read **without changing anything**.
2. **Before launching the subagents**, generate the `RECON.md` of the cloned directory with the [[.agents/skills/recon-project/SKILL|recon-project]] skill (`python3 scripts/pop_recon.py <dir>`) and read it first — pass it as context to each subagent, to reduce each front's manual sweep.
3. Launch **parallel subagents**, one per front: **(a)** structure and stack; **(b)** how it's built/tested/run (scripts, CI); **(c)** existing docs (README, docs/, key comments); **(d)** git history — activity, branches, commit conventions; **(e)** visible fragile or unfinished spots.
4. Consolidate a **short map** (≤30 lines) and present it to the user for correction before proceeding.

## Step 2 — Fit into the vault

Ask: **(a)** which **type** (explain using [[TYPES|TYPES]]): AI specs and harness committed in the repo itself → `uni-repo` (the clone at `projects/<project>/` **is** the project, with the whole `pop/` committed in it; a local project with no repo is also `uni-repo`, versioned in the PoP); it's one of several repos of the same project → `multi-repo` (a parent folder at `projects/<project>/` **with no harness** — one clone per repo at its root, each with its own complete `pop/`; no central kanban)? **(b)** what is the tasks' **PR branch**? **(c)** project name in kebab-case (propose one; it may differ from the repo name). **(d)** what is the **project's default language** — the recon indicates the current language of code and docs; confirm. Specs, notes, research, code comments and the flow follow that language (declared in the project's AGENTS.md). **(e)** if it is an application: which **languages must it support** (i18n) — the recon shows what i18n already exists; the confirmed list goes into the AGENTS.md and is handled in the roadmap and specs.

## Step 3 — Project flow (what makes the specs faithful)

Ask what the code doesn't show: **(a)** what the project does today, in the user's view — confront it with the recon map; **(b)** the main flows, end to end (input → processing → output; or the domain equivalent); **(c)** what works well vs. what is broken/unfinished; **(d)** historical decisions that explain the current design (they become `pop/notes/decisions/`); **(e)** how it is delivered/published today. **Divergence between recon and the user's answer → RECON NEEDED**, never pick a side on your own.

## Step 4 — Roadmap from the current point

1. **Epoch 1 — Organization (fixed):** propose the phases and candidate tasks to build the knowledge harness, e.g.: `1.1` specs of the current state (one per real topic, via `write-spec` — born as `draft` with a full "Open" section); `1.2` the project's operational skills (build, test, run, deploy — `pop/skills/`); `1.3` pending research (`pop/researches/`, resolving the RECON NEEDED items) and notes (`pop/notes/decisions|references`); **applications:** include the task to **initialize the DOX tree** (recursive sweep of the code — process in `_templates/DOX.md`, pasted into the project's AGENTS.md). RECON NEEDED that calls for deep research → prompt in the **`RESEARCHES.md`** (optional, `_templates/RESEARCHES.md`) for the user to run. The epoch's tasks generate the first `pop/memory/` entries.
2. **Following epochs:** follow the **`plan-roadmap`** skill for the project's future — the destination, given the current point.

## Step 5 — Materialization

1. Create the full structure as in `new-project` step 6 (anatomy per type, clones, `.gitignore`, index, Aggregated repositories according to the type). For each repo with a harness — a `uni-repo` with a repo and each repo of a `multi-repo` — run the same `python3 scripts/pop_install_unirepo.py <repo>`; don't re-copy inventories manually.
2. **Organization gate** — add to the "Essential rules" of the project's AGENTS.md:
   > **Imported project:** until Epoch 1 (Organization) is `completed` in the ROADMAP, no task may change the project's content (the folder root) or the repository — only the harness in `pop/` (specs, skills, researches, notes). A change request during this period → record it in `pop/notes/ideas/` or as a future-epoch task, explaining the gate.
3. **`pop/PROJECT.md`** receives the summarized recon map; **`pop/ROADMAP.md`** with Epoch 1 = Organization (the vault-root meta-project and not-yet-migrated projects: harness at the root, no `pop/`); the epoch file carries the **RECON NEEDED** items left open (with each one's check).
4. Project status in the indexes: `planning` (becomes `in progress` when the first organization task enters the kanban).
5. Close with a summary: project map, open questions and a suggestion for the first organization task (`new-task` skill).

## Cautions

- **Recon is read-only:** the import doesn't change the imported repo in any way — the first real change will only exist via the kanban, and only after Epoch 1.
- **Faithful spec = recon + user confirmation.** Don't write a spec from the code alone: what the user hasn't confirmed is born in the "Open" section.
- The organization gate applies to **any agent, always** — it is not a suggestion. Epoch 1 completes via the derived status (all tasks with a memory). Don't create tasks here (`new-task` skill) nor specs outside the flow (`write-spec` skill).
