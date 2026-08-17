---
author: user
date: 2026-08-16
---

# Harness decisions — 2026-08-16

## The kanban becomes optional

The kanban stops being mandatory and becomes optional. The agent recommends it when the change is large; outside the direct fix, the choice is the user's at the rule-13 triage.

**Rationale:** the kanban's ceremony pays off on work that needs planning and gates; forcing it on every change taxed small, well-understood work without adding protection.

## No-kanban route = the coding agent's plan mode

No card, stages or `pop_move` — but never without tracking: the ledger `memory/<YYYY-MM-DD>/D-YYYYMMDD-<slug>.md` + entries + specs/DOX assessment/sync stay mandatory. The `D-` ID stops meaning "deviation under a literal command" and becomes the legitimate route chosen in the triage. The route **has no yolo mode**: without a card there is no Judge Dredd, circuit breaker or gates — the human approves the plan and the result. The project's agents and skills (delegation-first, the six specialists, `clean-code-*`, `ui-*` etc.) keep applying — the route changes the tracking, not the standard of work.

**Rationale:** the old literal-waiver protocol made "skip the kanban" an exception that only a sovereign command could activate; in practice it is an ordinary routing choice. What must never be waived is continuity (memory + specs), so that stays mandatory on every route.

## Yolo and roadmap/modifications items imply the kanban by default

Implied, with a one-line notice ("this goes through the kanban") and no extra question. When in doubt, one one-line question decides.

**Rationale:** yolo delegates judgment to the Judge Dredd gate, which only exists on a card; a roadmap/modifications item is already planned kanban material.

## `full-multi-repo` loses the central kanban

The parent's `pop/` keeps only the general ROADMAP (+ transversal researches/notes) — no `kanban/`, `specs/` or `memory/`. A cross-repo task is sliced per repo and each slice lives in the affected repo's kanban (slug carries the repo name), with memory and specs recorded in the repo itself; the general ROADMAP links the sibling tasks with a trigger.

**Rationale:** two kanbans for the same work duplicated tracking and forced every cross-repo task to close in two places; each repo's harness is already complete and standalone.

## Contracts

- [[WORKFLOW|WORKFLOW]] — *follow for the triage, the no-kanban route and the yolo-implies-kanban default*.
- [[TYPES|TYPES]] — *follow for the full-multi-repo anatomy without a central kanban*.
- [[specs/harness-lifecycle|Harness lifecycle]] — *follow for the `D-` memory invariant*.
