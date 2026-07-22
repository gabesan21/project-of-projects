# PoP scripts

Python 3.9+, standard library only.

**Task ids:** two origins — roadmap `1.2.3-slug` (`<epoch>.<phase>.<task>`) and modifications `M-1.2-slug` (task `2` of modification `M-1`; frontmatter with `origin: modifications` + `modification: M-1`, no `epoch`/`phase`).

| Script | Purpose |
|---|---|
| `pop_status.py` | Kanban overview, pending gates, claims, circuit breakers, stale work, and merge waits. |
| `pop_claim.py` | Per-task lease preventing duplicate orchestrators. |
| `pop_validate.py` | Validates limits, cards (frontmatter per origin: roadmap requires `epoch`/`phase`; modifications requires `modification: M-<n>`), canonical specs, telemetry, standalone anatomy, links, hashes, and completed-task residue in the roadmap/modifications. |
| `pop_move.py` | Moves a task, updates card/log/telemetry, counts yolo returns, and opens the circuit on failure three. Non-critical yolo transits 002→004 directly (003 only for `critical: true`). |
| `pop_task.py` | Creates a task card from the template, filling the frontmatter block of the id's origin (roadmap or `M-`). |
| `pop_worktree.py` | Resolves route and manages task worktrees; root PoP refuses them, external yolo starts from `develop`. |
| `pop_roadmap.py` | `close` removes exactly one completed task row from the epoch or modification file after canonical memory; for a single-task modification it removes only the wikilink from the `MODIFICATIONS.md` row. `check/prune` audit/migrate residue. |
| `pop_yolo.py` | Safe waves up to three, verification mode, minimal telemetry, and human circuit reset. |
| `pop_delivery.py` | Idempotent external-yolo integration into `develop` and final `develop` → `main` PR creation/reuse. |
| `pop_check_scope.py` | Validates committed/local/untracked diff against ownership and deny globs. |
| `pop_install_included.py` | Installs/updates the manifest-defined standalone included package; audits manifest closure. |

Example:

```
python3 scripts/pop_task.py agents/my-project 1.1.1-user-table-creation --title "User table"
python3 scripts/pop_task.py agents/my-project M-1.1-adjust-contract --title "Adjust contract"
python3 scripts/pop_move.py M-1.1-adjust-contract 002_planning --reason "planning started"
```

Run `python3 -m unittest discover -s scripts/tests -v`, `python3 scripts/pop_install_included.py --audit-manifest`, and `python3 scripts/pop_validate.py` before delivery.
