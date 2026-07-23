---
task: <id>-<slug>
project: <category>/<project>
started: YYYY-MM-DD
finished: YYYY-MM-DD
commit: <final-commit-hash>
pr: <PR-link-or-explicitly-empty>
authorization: <only for D-YYYYMMDD-<slug>: human command that waived the kanban>
---

# <id>-<slug> — <short title>

> Durable ledger written and validated before removing the task from the roadmap and deleting `kanban/006_done/<id>/`. Total ≤2000 characters. Record facts and pointers instead of retelling planning or execution; use [[.agents/skills/optimize-memory/SKILL|optimize-memory]] if it grows without losing chronology or critical decisions. A literal human waiver of the kanban uses `task: D-YYYYMMDD-<slug>`, fills `authorization`, and has no card or roadmap row.

- **Delivery:** <observable result>.
- **Changed areas:** `<subtree/file>` — <one line>.
- **Verification:** <aggregate gate and result>.
- **Final telemetry:** <stage contexts; 003/005 returns; differential|full; final tests—no reasoning>.
- **Durable decisions:** none | <decision and short rationale>.
- **Relevant deviations:** none | <authorized difference from brief>.
- **Contract impact:** specs: <assessed; updated when affected> · DOX: <assessed; updated when affected>.

## Links

- **Affected spec:** [[categories/<category>/<project>/pop/specs/<spec>|<spec>]] — *follow for the changed contract*.
- **Learning:** [[categories/<category>/<project>/pop/notes/learnings/<note>|<note>]] — *follow when reusable*.
- **PR/commit:** <link/hash> — *follow to inspect the final diff*.
