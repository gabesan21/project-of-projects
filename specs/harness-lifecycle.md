---
id: harness-lifecycle
project: pop
domain: harness
kind: contract
status: active
implementation: implemented
origin: "7.1"
created: 2026-07-21
updated: 2026-07-21
supersedes: []
superseded_by:
---

# Spec — Harness lifecycle

## Contract

Roadmaps show structure and open work; `memory/` preserves chronological proof; Git delivery distinguishes a local root PoP from coordinated external repositories.

## Expected behavior

- `ROADMAP.md` lists epochs; epoch files list phases and open tasks only. `MODIFICATIONS.md` lists modifications (one line each; completed rows stay); modification files list open tasks only.
- In 006, after valid memory/spec/status updates and before deleting the card, `pop_roadmap.py close` removes exactly one task row from the epoch or modification file while preserving epoch, phase, modification, and open tasks.
- Weekly review reports completed-task residue and memory candidates; `optimize-memory` never merges ledgers or removes chronology/critical decisions.
- A root local PoP (`project: pop`, kanban at root) works directly on `main`, without its own task branch/worktree/PR.
- External yolo tasks integrate idempotently into `develop`; the final scope opens/reuses `develop` → `main`, and only the human merges.

## Invariants

- No task row is removed without a canonical same-ID memory containing project, dates, commit, and an explicit `pr` key.
- Memory preserves one file per task, identity, dates, commit/PR, event order, and critical decisions.
- Epochs, phases and modifications are never removed as a task-completion side effect.
- Conflicts, missing branches/tools, dirty worktrees, or PR failure block without autonomous resolution/merge.
- External clones change only in their own authorized task.

## Conformance

- [x] `pop_roadmap.py`, `pop_worktree.py`, and `pop_delivery.py` provide deterministic operations.
- [x] Roadmap, route, memory, duplicate, and delivery regressions pass.
- [x] [[.agents/skills/optimize-memory/SKILL|optimize-memory]] preserves irreducible history.
