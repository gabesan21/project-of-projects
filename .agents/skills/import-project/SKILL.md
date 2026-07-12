---
name: import-project
description: Imports an existing repository or project into the vault - codebase recon, fit interview (type, category) and a mandatory Epoch 1 of organization (faithful specs, skills, research, notes), with a gate that blocks changes to the project until it completes. Use when the user asks to import/add an existing project or repository to the PoP.
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
2. Launch **parallel subagents**, one per front: **(a)** structure and stack; **(b)** how it's built/tested/run (scripts, CI); **(c)** existing docs (README, docs/, key comments); **(d)** git history — activity, branches, commit conventions; **(e)** visible fragile or unfinished spots.
3. Consolidate a **short map** (≤30 lines) and present it to the user for correction before proceeding.

## Step 2 — Fit into the vault

Ask: **(a)** which category (in `categories/`: `agents` | `applications` | `writing` | `work` — or a new one)? **(b)** which **type** (explain using TYPES.md): AI specs can be committed to the repo → `included`; repo must stay clean of harness → `default` (clone in `project/`); it's one of several repos of the same project → `multi-repo`; several repos that must work standalone, each with a harness committed inside → `full-multi-repo`? **(c)** what is the tasks' **PR branch**? **(d)** project name in kebab-case (propose one; it may differ from the repo name). **(e)** what is the **project's default language** — the recon indicates the current language of code and docs; confirm. Specs, notes, research, code comments and the flow follow that language (declared in the project's AGENTS.md). **(f)** if it is an application: which **languages must it support** (i18n) — the recon shows what i18n already exists; the confirmed list goes into the AGENTS.md and is handled in the roadmap and specs.

## Step 3 — Project flow (what makes the specs faithful)

Ask what the code doesn't show: **(a)** what the project does today, in the user's view — confront it with the recon map; **(b)** the main flows, end to end (input → processing → output; or the domain equivalent); **(c)** what works well vs. what is broken/unfinished; **(d)** historical decisions that explain the current design (they become `notes/decisions/`); **(e)** how it is delivered/published today. **Divergence between recon and the user's answer → RECON NEEDED**, never pick a side on your own.

## Step 4 — Roadmap from the current point

1. **Epoch 1 — Organization (fixed):** propose the phases and candidate tasks to build the knowledge harness, e.g.: `1.1` specs of the current state (one per real topic, via `write-spec` — born as `draft` with a full "Open" section); `1.2` the project's operational skills (build, test, run, deploy — `skills/`); `1.3` pending research (`researches/`, resolving the RECON NEEDED items) and notes (`notes/decisions|references`); **applications:** include the task to **initialize the DOX tree** (recursive sweep of the code — process in `_templates/DOX.md`, pasted into the project's AGENTS.md). RECON NEEDED that calls for deep research → prompt in the **`RESEARCHES.md`** (optional, `_templates/RESEARCHES.md`) for the user to run. The epoch's tasks generate the first `memory/` entries.
2. **Following epochs:** follow the **`plan-roadmap`** skill for the project's future — the destination, given the current point.

## Step 5 — Materialization

1. Create the full structure as in `new-project` step 6 (anatomy per type, clones, `.gitignore`, indexes, Aggregated repositories when `included`/`multi-repo`/`full-multi-repo`).
2. **Organization gate** — add to the "Essential rules" of the project's AGENTS.md:
   > **Imported project:** until Epoch 1 (Organization) is `completed` in the ROADMAP, no task may change `project/` or the repository — only the harness (specs, skills, researches, notes). A change request during this period → record it in `notes/ideas/` or as a future-epoch task, explaining the gate.
3. **PROJECT.md** receives the summarized recon map; **ROADMAP.md** with Epoch 1 = Organization; the epoch file carries the **RECON NEEDED** items left open (with each one's check).
4. Project status in the indexes: `planning` (becomes `in progress` when the first organization task enters the kanban).
5. Close with a summary: project map, open questions and a suggestion for the first organization task (`new-task` skill).

## Cautions

- **Recon is read-only:** the import doesn't change the imported repo in any way — the first real change will only exist via the kanban, and only after Epoch 1.
- **Faithful spec = recon + user confirmation.** Don't write a spec from the code alone: what the user hasn't confirmed is born in the "Open" section.
- The organization gate applies to **any agent, always** — it is not a suggestion. Epoch 1 completes via the derived status (all tasks in `006_done`/memory). Don't create tasks here (`new-task` skill) nor specs outside the flow (`write-spec` skill).
