# scripts — vault CLI

Scripts in **Python 3 (≥3.9), stdlib only** — agent-agnostic and cross-platform (`pathlib`). They replace manual agent sweeps with 1 command. All accept `--vault DIR` (default: folder above `scripts/`) and `--help`.

| Script | Does |
|--------|-----|
| `pop_status.py` | Overview: tasks per stage/project, pending gates (release in 001, 003, 005 critical, merge), blocked, stale >14 days, active claims, WIP > 3 alert. `--project <cat>/<proj>` filters. |
| `pop_claim.py <task>` | Task claim (lease) — one agent per task: writes `claimed_by:`/`claimed_at:` to the card; active claim by another agent → refusal (exit 1); a 2h lease expires an orphan claim. `--release` releases, `--status` queries, `--by` identifies the agent. |
| `pop_validate.py` | Validates limits: 144/600 chars in the indexes, ≤150 lines per note (plans ≤200; research `raw/` exempt), card frontmatter, consistent `stage:`; warnings: orphan worktrees and broken wikilinks. Exit 1 on violation. |
| `pop_move.py <task> <stage>` | Moves the task folder, validates the transition (returns: 003→002, 004→002, 005→004; `--force` for exceptions), updates `stage:`/`updated:` and the `## Log` (`--reason`). Refuses a task with another agent's active claim (`--by`) and 001→002 without `- [x] Ready to plan`. |
| `pop_task.py <cat>/<proj> <id>` | Scaffolding: card in `001_initial_task` from `_templates/TASK.md` + empty `subtasks/`. `--title "..."` sets the title. Embedded repo of a `full-multi-repo`: `<cat>/<proj>/<repo>`. |
| `pop_worktree.py add\|remove <task>` | Creates/removes `worktrees/<id>` + branch `task/<id>` via git. Target repo: `--repo` (a path, or a **clone name** in `project/<name>/` → nested worktree `worktrees/<id>/<name>/`, for a cross task of `multi-repo`/`full-multi-repo`); default: the project folder if it is a git repo (included/embedded repo), otherwise the vault root. `--base`, `--delete-branch`. |

`poplib.py` is the shared module: vault root, project discovery (globs `categories/*/*/kanban/` and `categories/*/*/project/*/kanban/` — embedded repos of `full-multi-repo`; labels `<cat>/<proj>` or `<cat>/<proj>/<repo>`, always relative to `categories/` and without the `project/` segment) and its own frontmatter parser (no PyYAML).

Example:

```
python3 scripts/pop_task.py agents/my-project 1.1.1-user-table-creation --title "User table"
python3 scripts/pop_move.py 1.1.1-user-table-creation 002_planning --reason "plan started"
python3 scripts/pop_status.py
```
