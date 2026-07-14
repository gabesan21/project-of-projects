# TYPES — project types

The PoP is a **repository aggregator**: each project declares a `type` in its own `AGENTS.md` (template [[_templates/AGENTS-PROJECT|AGENTS-PROJECT]]). Since 2026-07-14 the anatomy is the same for all of them: **the PoP harness lives in the `pop/` subfolder** and the project's content sits at the **root** of the folder (the root holds only `AGENTS.md`, `CLAUDE.md`, `.agents/skills/`, `.gitignore` and the content). The type defines two things: **where the repository(ies) live(s)** and **which `pop/` owns which kanban**. General rules: [[AGENTS|AGENTS]] · Flow: [[WORKFLOW|WORKFLOW]].

> **Transition:** projects created before 2026-07-14 still use the legacy anatomy (harness at the folder root and content in `project/`) until migration; the `pop_*` scripts support both.

## Quick view

| Type | Project root (content) | `pop/` | Repository(ies) |
|------|------------------------|--------|-----------------|
| `default` | folder in the vault (`categories/<category>/<project>/`) | versioned in the PoP | optional — declared **only in the project's AGENTS.md** |
| `included` | the **external repo itself** (the vault folder is the gitignored clone) | committed **in the repo** | optional — if any, it goes into **Aggregated repositories** in the root [[INDEX|INDEX]] |
| `multi-repo` | folder in the vault with **one clone per repo at the root** (gitignored) | versioned in the PoP, single kanban | **required** — all in the project's AGENTS.md **and** in the root INDEX |
| `full-multi-repo` | like multi-repo, but each clone brings its **own `pop/`** `included`-style | parent: only general ROADMAP + cross-repo kanban | **required** — all in the project's AGENTS.md **and** in the root INDEX |

**Reserved names:** no repo/content folder at a project's root may be called `pop` (collides with the harness) or `project` (collides with legacy-anatomy discovery during the transition).

## default

The PoP's default. The project's folder in the vault carries the harness in `pop/` and the content (code, manuscript etc., free structure) directly at the root.

- **Without an external repo:** root and `pop/` versioned in the PoP repository itself.
- **With an external repo:** the repo and the PR branch are declared **only in the project's AGENTS.md** — not in the PoP's master list; if there is a local clone, it goes into the project's `.gitignore`. The PoP harness is **never committed** into the external repo — it stays clean of AI files.

## included

The project's root **is the external repository**: the whole `pop/` (including `WORKFLOW.md`, `TYPES.md`, `INBOX.md`, `_templates/` and `scripts/`) is committed in the repo, with `AGENTS.md` and `.agents/skills/` at the root. It's the type for those who want the PoP workflow traveling with their own repo, working standalone for people who don't even use the PoP — and the dev sees only `AGENTS.md`, `.agents/` and a `pop/` folder.

- **With a repo:** the repo is cloned into `categories/<category>/<project>/` and listed in **Aggregated repositories** in the root [[INDEX|INDEX]]; the clone's path goes into the PoP's **root** `.gitignore` (the PoP doesn't version the content — only the index entry). Materialization uses `python3 scripts/pop_install_included.py <repo>`; the manifest is the package's single list and updating repeats the same command.
- **Without a repo:** the project's folder in the PoP is the project root itself, versioned in the PoP.

## multi-repo

Like `default`, but the folder root contains **multiple repositories**, one subdirectory per repo (`<repo-a>/`, `<repo-b>/`), all cloned and gitignored in the project's `.gitignore`. The harness (single kanban, specs, memory…) lives in the project's `pop/`, versioned in the PoP.

- Declare **all** repos (URL, path, PR branch) in the project's AGENTS.md **and** in Aggregated repositories in the root INDEX.
- Worktrees: one per repository affected by the task, in `pop/worktrees/<task-id>/<repo>/` — see [[WORKFLOW|WORKFLOW]].

## full-multi-repo

Like `multi-repo` in the main folder, but each repo cloned at the root carries its **own embedded harness** (a full `included` installation in `<repo>/pop/`, committed in the repo): individual kanban, specs, memory, notes, skills, researches and ROADMAP. The set becomes a **logical monorepo**: whoever works on a single repo (e.g. a frontend dev) uses that repo's `pop/`, standalone; whoever works on the whole uses the main folder in the PoP.

- **Main folder (in the PoP):** AGENTS.md, and in the parent's `pop/`: sheet, general ROADMAP + `roadmap/` (macro epochs whose phases point, with a trigger, to the individual ROADMAPs or to cross tasks), `kanban/` **for cross-repo tasks only**, `worktrees/` of those tasks, transversal `researches/` and `notes/`. **No `specs/` and no `memory/`** — they always live in the repos.
- **Each repo:** full `included` anatomy; the repo's AGENTS.md declares `type: included` (the standalone truth) + a **"Part of"** section linking the parent project, the general ROADMAP and the cross kanban.
- **Single-repo task** → the repo's own kanban, worktree in `pop/worktrees/<id>/` inside the repo (the repo is its own git).
- **Cross-repo task** → central kanban; one worktree per affected repo in `pop/worktrees/<id>/<repo>/` in the parent (as in `multi-repo`); on completion (006), write `pop/memory/<id>.md` in **each affected repo** and sync the specs **in the repos** — the central card links those memories.
- **Contract specs between repos** (e.g. front↔back API) live in the repo that "owns" the contract; the others link to it.
- **Task slugs carry the repo name** (e.g. `1.2.1-front-login-page`): ids are unique across the whole vault and the scripts locate tasks by id.
- Clones gitignored in the project's `.gitignore`; `pop/worktrees/` gitignored in each repo's `.gitignore`.

## What `new-project` creates per type

| Step | default | included | multi-repo | full-multi-repo |
|------|---------|----------|------------|-----------------|
| `AGENTS.md` + `.agents/skills/` (root) + `pop/` (full harness) | in the PoP | inside the repo (or in the PoP, without a repo) | in the PoP | reduced `pop/` in the parent (no specs/memory) + full `included` inside each repo |
| `.agents/skills/` | real copies of the core skills | real copies of the core skills | real copies of the core skills | copies in the main folder **and** in each repo |
| Clone(s) | optional, at the project root (if any) | `categories/<category>/<project>/` | `<repo>/` at the project root, for each | `<repo>/` at the project root, for each |
| Project `.gitignore` | `pop/worktrees/` + clone | `pop/worktrees/` | `pop/worktrees/` + clones | `pop/worktrees/` + clones (each repo ignores its own `pop/worktrees/`) |
| PoP root `.gitignore` | — | clone path | — | — |
| Aggregated repositories (root INDEX) | — | repo (if any) | all repos | all repos |
