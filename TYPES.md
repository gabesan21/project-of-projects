# TYPES — project types

The PoP is a **repository aggregator**: each project declares a `type` in its own `AGENTS.md` (template [[_templates/AGENTS-PROJECT|AGENTS-PROJECT]]), which defines where the real work lives, where the PoP harness sits and where repositories are declared. General rules: [[AGENTS|AGENTS]] · Flow: [[WORKFLOW|WORKFLOW]].

## Quick view

| Type | `project/` folder | PoP harness | Repository(ies) |
|------|-------------------|-------------|-----------------|
| `default` | exists: real work or clone of the external repo | in `categories/<category>/<project>/`, outside `project/` | optional — declared **only in the project's AGENTS.md** |
| `included` | **does not exist** | at the **root of the project's repository**, alongside the other files | optional — if any, it goes into **Aggregated repositories** in the root [[INDEX|INDEX]] |
| `multi-repo` | contains **multiple repositories**, one subdirectory per repo | in `categories/<category>/<project>/` | **required** — all in the project's AGENTS.md **and** in the root INDEX |

## default

The PoP's default. The harness (kanban, roadmap, specs, notes, memory…) lives in `categories/<category>/<project>/` inside the PoP repository; the real work lives in `project/`.

- **Without an external repo:** `project/` is versioned in the PoP repository itself.
- **With an external repo:** `project/` receives the clone (`project/<repo-name>/`), listed in the project's `.gitignore`. The repo and the PR branch are declared **only in the project's AGENTS.md** — not in the PoP's master list. The PoP harness is **never committed** into `project/` files — the external repo stays clean of AI specs.

## included

The PoP harness lives **inside the project's repository**, at the root, mixed with the other files — there is no `project/` subfolder. It's the type for those who want the PoP workflow committed in their own repo, working standalone for people who don't even use the PoP.

- **With a repo:** the repo is cloned into `categories/<category>/<project>/` and listed in **Aggregated repositories** in the root [[INDEX|INDEX]]; the clone's path goes into the PoP's **root** `.gitignore` (the PoP doesn't version the content — only the index entry). The `new-project` skill copies into the repo: `AGENTS.md` (+ `CLAUDE.md` symlink), `.agents/skills/` (**real copies** of the core skills), `_templates/`, `WORKFLOW.md`, `TYPES.md` and the anatomy folders.
- **Without a repo:** the project's folder in the PoP is the project root itself, versioned in the PoP.

## multi-repo

Like `default`, but `project/` contains **multiple repositories**, one subdirectory per repo (`project/<repo-a>/`, `project/<repo-b>/`), all cloned and gitignored in the project's `.gitignore`.

- Declare **all** repos (URL, path, PR branch) in the project's AGENTS.md **and** in Aggregated repositories in the root INDEX.
- Worktrees: one per repository affected by the task, in `worktrees/<task-id>/<repo>/` — see [[WORKFLOW|WORKFLOW]].

## What `new-project` creates per type

| Step | default | included | multi-repo |
|------|---------|----------|------------|
| Standard anatomy (AGENTS.md, .agents/, memory/, worktrees/, kanban/…) | in the PoP | inside the repo (or in the PoP, without a repo) | in the PoP |
| `.agents/skills/` | real copies of the core skills | real copies of the core skills | real copies of the core skills |
| Clone(s) | `project/<repo>/` (if any) | `categories/<category>/<project>/` | `project/<repo>/` for each |
| Project `.gitignore` | `worktrees/` + clone | `worktrees/` | `worktrees/` + clones |
| PoP root `.gitignore` | — | clone path | — |
| Aggregated repositories (root INDEX) | — | repo (if any) | all repos |
