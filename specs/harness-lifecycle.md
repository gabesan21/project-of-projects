---
id: harness-lifecycle
project: pop
domain: harness
kind: contract
status: active
implementation: implemented
origin: "7.1"
created: 2026-07-21
updated: 2026-07-27
supersedes: []
superseded_by:
---

# Spec — Harness lifecycle

## Contract

Roadmaps show structure and open work; `memory/` preserves chronological proof in folders per completion date; Git delivery distinguishes a local root PoP from coordinated external repositories.

## Expected behavior

- `ROADMAP.md` lists epochs; epoch files list phases and open tasks only. `MODIFICATIONS.md` lists modifications (one line each; completed rows stay); modification files list open tasks only.
- In `005_closing`, after valid memory/spec/status updates and before deleting the card, `pop_roadmap.py close` removes exactly one task row from the epoch or modification file while preserving epoch, phase, modification, and open tasks.
- `005_closing` gathers quality gate, delivery, and close-out: in yolo the gate is one fresh `pop-judge-dredd` with a fixed native profile at every `size` ([[specs/judge-dredd|contract]]); outside yolo the gate is the human PR, and with no PR there is no verification gate. Close-out is mechanical and idempotent.
- Every memory lives in `memory/<YYYY-MM-DD>/`, where the folder is the completion date and equals `finished`: one **ledger** `<id>.md` (≤1200 characters) per task, carrying the proof frontmatter and the index of the entries, and one **entry** `<id>.<nn>-<slug>.md` (≤800 characters) per thing done, numbered chronologically and carrying at least one wikilink to the spec or the file that attests the change. Form: [[_templates/MEMORY|MEMORY]] and [[_templates/MEMORY-ENTRY|MEMORY-ENTRY]].
- Flat memory in `memory/<id>.md` with `finished` earlier than 2026-07-27 is tolerated legacy; from that date on the folder layout is mandatory.
- Weekly review reports completed-task residue and memory candidates; `optimize-memory` converts legacy memory into that layout and trims whatever exceeds the cap, never merging ledgers or removing chronology/critical decisions.
- A root local PoP (`project: pop`, kanban at root) works directly on `main`, without its own task branch/worktree/PR.
- External yolo tasks integrate idempotently into `develop`; the final scope opens/reuses `develop` → `main`, and only the human merges.

## Invariants

- **Harness maintenance does not go through the kanban.** Managed harness is fixed at the origin and arrives by reinstallation; the scope's own harness (`AGENTS.md`, sheet, roadmap, specs, notes, skills, `memory/`) is adjusted directly, with no card, branch, worktree or task PR. The kanban gates content; submitting to it the material it consults is asking the process to approve itself. The three classes are in [[WORKFLOW|WORKFLOW]] › "Current scope".
- The project AGENTS.md ruler **always measures**: in an application the DOX block is discounted and the remaining excess is reported as a warning. An exemption that switches the measurement off turns a cap into invisible debt.
- No task row is removed without a canonical same-ID memory containing project, dates, commit, and an explicit `pr` key.
- No close-out effect — memory, spec sync, `close`, folder deletion — happens before gate approval when the gate exists; a circuit breaker or an unapproved gate never starts close-out.
- A task dependency is satisfied only by the memory ledger; there is no per-stage transitional window.
- Each completed task keeps exactly one ledger of its own, with its entries subordinated to it; optimization never merges, removes or renames tasks. Memory preserves identity, dates, commit/PR, event order, and critical decisions.
- An entry with no ledger in the same folder, or not indexed by it, is orphaned and invalid; an entry with no evidence wikilink is an assertion, not proof.
- Epochs, phases and modifications are never removed as a task-completion side effect.
- Conflicts, missing branches/tools, dirty worktrees, or PR failure block without autonomous resolution/merge; partial close-out failure preserves card and roadmap, records the blocking step, and retries from the first incomplete effect.
- External clones change only in their own authorized task.
- The no-kanban route (plan mode) without identifiable memory (`D-`) does not authorize writing; contracts are edited only when the assessment records real impact.

## Conformance

- [x] `pop_roadmap.py`, `pop_worktree.py`, and `pop_delivery.py` provide deterministic operations.
- [x] Roadmap, route, memory, duplicate, and delivery regressions pass.
- [x] `weekly-review` and `optimize-memory` run outside the kanban, in parallel waves with disjoint write sets, and the review fixes unambiguous scope-owned harness instead of only proposing.
- [x] The validator measures every application's AGENTS.md with the DOX block discounted, and reports the excess as a warning.
- [x] [[.agents/skills/optimize-memory/SKILL|optimize-memory]] preserves irreducible history in one ledger per task.
- [x] The validator rejects a ledger/entry above the cap, an orphaned entry, an entry with no evidence, and new memory outside a date folder.
