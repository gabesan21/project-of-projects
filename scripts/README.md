# PoP scripts

Python 3.9+, standard library only.

**Task ids:** two origins — roadmap `1.2.3-slug` (`<epoch>.<phase>.<task>`) and modifications `M-1.2-slug` (task `2` of modification `M-1`; frontmatter with `origin: modifications` + `modification: M-1`, no `epoch`/`phase`).

| Script | Purpose |
|---|---|
| `pop_status.py` | Kanban overview, pending gates, claims, circuit breakers, stale work, and merge waits. |
| `pop_claim.py` | Per-task lease preventing duplicate orchestrators. |
| `pop_validate.py` | Validates limits, the freshness of the harness installed in the projects (`content_sha` stamp vs. source — stale is a violation), cards (frontmatter per origin: roadmap requires `epoch`/`phase`; modifications requires `modification: M-<n>`), canonical specs, telemetry, standalone anatomy, links, hashes, and completed-task residue in the roadmap/modifications. |
| `pop_move.py` | Moves a task, updates card/log/telemetry, counts yolo returns, and opens the circuit on failure three. Non-critical yolo transits 002→004 directly (003 only for `critical: true`). A return leaving `005_closing` records the cause in `return_kind`: `--return-kind lacuna\|premissa` is required for →002; →004 assumes `execucao`. |
| `pop_task.py` | Creates a task card from the template, filling the frontmatter block of the id's origin (roadmap or `M-`). |
| `pop_worktree.py` | Resolves route and manages task worktrees; root PoP refuses them, external yolo starts from `develop`. |
| `pop_roadmap.py` | At the close of `005_closing`, `close` removes exactly one completed task row from the epoch or modification file after canonical memory; for a single-task modification it removes only the wikilink from the `MODIFICATIONS.md` row. `check/prune` audit/migrate residue. |
| `pop_yolo.py` | Safe waves up to three, verification mode, minimal telemetry, and human circuit reset. `verify-mode` picks `full` only for `critical` or a `premissa` return; on other returns the differential covers the delta. `telemetry` sums the returns per cause (`returns_lacuna\|premissa\|execucao`). |
| `pop_delivery.py` | Idempotent external-yolo integration into `develop` and final `develop` → `main` PR creation/reuse. |
| `pop_check_scope.py` | Validates committed/local/untracked diff against ownership and deny globs. |
| `pop_install_included.py` | Installs/**updates** the harness declared in `_templates/included-manifest.json`: mirrors the managed set into the target and writes into it the source's `content_sha` plus the **inventory** of what it wrote. The next update's prune reaches only that inventory — a managed directory is not an exclusive one, so the project's own files under `pop/scripts/` stay. `--check-fresh <dir>` recomputes it and fails closed when the target has fallen behind (`pop_validate` reports it as a violation); `--sha` prints the source's version — both refuse with exit 2 when run from the installed copy, which is not the source; `--check` only checks whether it is installed; `--audit-manifest` audits manifest closure. |

Example:

```
python3 scripts/pop_task.py agents/my-project 1.1.1-user-table-creation --title "User table"
python3 scripts/pop_task.py agents/my-project M-1.1-adjust-contract --title "Adjust contract"
python3 scripts/pop_move.py M-1.1-adjust-contract 002_planning --reason "planning started"
```

Run `python3 -m unittest discover -s scripts/tests -v`, `python3 scripts/pop_install_included.py --audit-manifest`, and `python3 scripts/pop_validate.py` before delivery.
