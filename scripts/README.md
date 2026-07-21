# PoP scripts

Python 3.9+, standard library only.

| Script | Purpose |
|---|---|
| `pop_status.py` | Kanban overview, pending gates, claims, circuit breakers, stale work, and merge waits. |
| `pop_claim.py` | Per-task lease preventing duplicate orchestrators. |
| `pop_validate.py` | Validates limits, cards, canonical specs, telemetry, standalone anatomy, links, hashes, and completed-task roadmap residue. |
| `pop_move.py` | Moves a task, updates card/log/telemetry, counts yolo returns, and opens the circuit on failure three. |
| `pop_task.py` | Creates a task card from the template. |
| `pop_worktree.py` | Resolves route and manages task worktrees; root PoP refuses them, external yolo starts from `develop`. |
| `pop_roadmap.py` | `close` removes exactly one completed task row after canonical memory; `check/prune` audit/migrate residue. |
| `pop_yolo.py` | Safe waves up to three, verification mode, minimal telemetry, and human circuit reset. |
| `pop_delivery.py` | Idempotent external-yolo integration into `develop` and final `develop` → `main` PR creation/reuse. |
| `pop_check_scope.py` | Validates committed/local/untracked diff against ownership and deny globs. |
| `pop_install_included.py` | Installs/updates the manifest-defined standalone included package; audits manifest closure. |

Run `python3 -m unittest discover -s scripts/tests -v`, `python3 scripts/pop_install_included.py --audit-manifest`, and `python3 scripts/pop_validate.py` before delivery.
