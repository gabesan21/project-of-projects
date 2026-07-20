---
author: user
date: 2026-07-20
---

# Harness decisions — 2026-07-20

## Brief instead of prescriptive wargame

The planner remains separate from the executor to reduce context contamination and enable different models per role. `.plan.md` stores only the planning result: objective, strategy, areas, fronts, dependencies, contracts, material risks and criteria. Reasoning, pseudocode, speculative snippets, micro-edits and narrated red-team work are not artifacts.

## Adaptive execution by fronts

004 uses an execution orchestrator that chooses one executor, sequential specialists or parallel waves. Each front has an ephemeral contract with `owns`, `may_read`, `must_not_edit`, `depends_on`, expected input, skill and criterion. Parallelism requires logical and write independence; missing dependencies become `BLOCKED`, never opportunistic implementation. Parallel workers use isolated branches/worktrees and only the orchestrator integrates after `scripts/pop_check_scope.py` validates the diff.

## One independent reviewer

Verification and critique become one 005 role: compare objective/specs with diff, tests, behavior and quality, using blocking/suggestion/nit severity. `critical` raises tier/depth, not reviewer count. In yolo, the same role judges 003 and 005, but 005 starts in a clean session; mechanical `develop` integration in 006 belongs to the orchestrator.

## Proportional specs and memory

A spec describes a durable contract — behavior, invariants, interfaces, errors and conformance — without contingent internal solutions. A task that only restores an existing contract creates no new spec. Memory is a ledger ≤2000 characters; persisted subtasks are optional ownership fronts, not implementation steps.

Full contract: [[specs/multi-agent-orchestration|multi-agent orchestration]] — *follow when changing workflow, templates, skills or ownership validation*.
