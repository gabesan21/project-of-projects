# TYPES — project types

The PoP is a **repository aggregator**: each project declares a `type` in its own `AGENTS.md` (template [[_templates/AGENTS-PROJECT|AGENTS-PROJECT]]). There are exactly **two types**: `uni-repo` and `multi-repo` — settled in the sovereign decisions of 2026-08-18 ([[notes/decisions/2026-08-18-harness-decisions|harness decisions]]), which replaced the previous model **with no backwards compatibility** (one-time migration; the historical reference is the decisions note, not this document). The type defines two things: **where the repository(ies) live(s)** and **which `pop/` owns which kanban**. General rules: [[AGENTS|AGENTS]] · Flow: [[WORKFLOW|WORKFLOW]].

Projects live in **`projects/`** — one folder per project, with no intermediate category level.

## Quick view

| Type | Project root (content) | `pop/` | Repository(ies) |
|------|------------------------|--------|-----------------|
| `uni-repo` | the folder at `projects/<project>/` **is the repository itself** (or a free root, without a repo) | committed **in the repo** (no repo: versioned in the PoP) | optional — if any, it goes into **Aggregated repositories** in the root [[INDEX|INDEX]] |
| `multi-repo` | parent folder at `projects/<project>/` with **one clone per repo at the root** (gitignored) | **the parent has no `pop/`** — each repo carries its own, committed in it | **required** — all referenced in the parent's INDEX.md **and** in Aggregated repositories in the root INDEX |

**Reserved names:** no repo/content folder at a project's root may be called `pop` (collides with the harness) or `project` (reserved name of the anatomy).

## uni-repo

The project's folder **is the repository**: the whole `pop/` (with `WORKFLOW.md`, `TYPES.md`, `INBOX.md`, `_templates/` and `scripts/`) is committed in the repo, with `AGENTS.md` and `.agents/skills/` at the root. It's the type for those who want the PoP workflow traveling with their own repo, working standalone for people who don't even use the PoP — and the dev sees only `AGENTS.md`, `.agents/` and a `pop/` folder.

- **With a repo:** the repo is cloned into `projects/<project>/` and listed in **Aggregated repositories** in the root [[INDEX|INDEX]]; the clone's path goes into the PoP's **root** `.gitignore` (the PoP doesn't version the content — only the index entry). Materialization uses `python3 scripts/pop_install_unirepo.py <repo>`; the manifest (`unirepo-manifest.json`) is the package's single list, the `pop/.unirepo-harness.json` marker identifies the installation, and updating repeats the same command.
- **Without a repo:** the project's folder at `projects/<project>/` is the project root itself, versioned in the PoP — content and harness live together in it, with no external repository.

## multi-repo

A **parent folder without a harness** aggregating several repositories, each with its own complete `pop/`. The set becomes a **logical monorepo**: whoever works on a single repo (e.g. a frontend dev) uses that repo's `pop/`, standalone; whoever works on the whole uses the parent folder in the PoP.

- **Parent folder (in the PoP):** only `AGENTS.md`, `INDEX.md` (references the repos) and a general `ROADMAP.md`, **reserved for cross-repo plans**. **No `pop/`, no kanban, no specs and no memory** — tasks, specs and memory always live in the repos; there is no central kanban. Epochs go into the repos' ROADMAPs at planning/execution time.
- **Each repo:** full `uni-repo` anatomy (individual kanban, specs, memory, notes, skills, researches and ROADMAP), committed in the repo; the repo's AGENTS.md declares `type: uni-repo` (the standalone truth) + a **"Part of"** section linking the parent project and the general ROADMAP.
- **Single-repo task** → the repo's own kanban, worktree in `pop/worktrees/<id>/` inside the repo (the repo is its own git).
- **Cross-repo task** → sliced per repo: each slice lives in the affected repo's kanban, with the slug carrying the repo name (e.g. `1.2.1-front-login-page`), and the parent's general ROADMAP links the sibling tasks with a trigger. Each repo records its own memory and syncs its own specs when completing its slice.
- **Contract specs between repos** (e.g. front↔back API) live in the repo that "owns" the contract; the others link to it.
- **Task slugs carry the repo name** (e.g. `1.2.1-front-login-page`): ids are unique across the whole vault and the scripts locate tasks by id.
- Clones gitignored in the parent's `.gitignore`; `pop/worktrees/` gitignored in each repo's `.gitignore`.

## What `new-project` creates per type

| Step | uni-repo | multi-repo |
|------|----------|------------|
| `AGENTS.md` + `.agents/skills/` + `pop/` (full harness) | inside the repo (or in the PoP, without a repo) | parent: only `AGENTS.md` + `INDEX.md` + general `ROADMAP.md`; full `pop/` inside each repo |
| `.agents/skills/` | real copies of the core skills | real copies in each repo (the parent has none) |
| Clone(s) | `projects/<project>/` **is** the clone (if there is a repo) | `<repo>/` at the parent's root, one per repo |
| Project/parent `.gitignore` | `pop/worktrees/` | clones at the parent's root; each repo ignores its own `pop/worktrees/` |
| PoP root `.gitignore` | clone path (if there is a repo) | — |
| Aggregated repositories (root INDEX) | repo (if any) | all repos |
