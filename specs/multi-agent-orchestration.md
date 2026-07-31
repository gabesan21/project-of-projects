---
id: multi-agent-orchestration
project: pop
domain: harness
kind: contract
status: active
implementation: implemented
origin: "4.2"
created: 2026-07-20
updated: 2026-07-27
supersedes: []
superseded_by:
---

# Spec — Multi-agent kanban orchestration

## Contract

Planning, execution, and review use distinct contexts. Cards persist a sufficient brief and minimal telemetry; heavy reasoning, prompts, and discarded attempts remain ephemeral.

## Expected behavior

- 002 always uses a separate planner; the `005_closing` gate runs in **one** of two configurations per round, never both: **configuration B** — exactly one fresh independent reviewer — for non-critical yolo `size: S`/`M`; **configuration A** — the devil's advocate and, after them, the judge — when `yolo: true` and (`size: L` or `critical: true`), replacing the single reviewer in that round. Outside yolo neither exists: the gate is the human PR, and with no PR (root local PoP) there is no verification gate.
- The plan root fits in 80 lines at any `size`; every front destined for a separate context gets its own file of at most 50 lines in `subtasks/`.
- A cohesive 004 front receives a direct executor. DAGs, multiple skills, or disjoint write sets receive a sub-orchestrator with explicit contracts.
- In yolo, the `005_closing` gate is the **single quality gate**: the live configuration's judge — the single reviewer in B, the judge in A — is strong in a fresh session, first checks whether the original request was met and, on approval, writes the memory in the same session; 003 with a strong critic exists only for `critical: true`. The gate has three exits: approved, execution blocker (→004), and plan defect (→002). Each route permits two automatic returns; failure three on the same route opens a circuit breaker requiring human intervention.
- Every return names a delta — type, affected criteria, fronts re-entering, and untouched fronts — classified in `return_kind` (`lacuna` | `premissa` | `execucao`) by `pop_move`. Re-entry into 004 executes only the delta's fronts; re-review is differential over it, and `full` is reserved for `critical: true` and a `premissa` return.
- A `lacuna` return amends the plan additively: criteria and fronts are append-only between rounds, because their IDs are referenced by verification and telemetry.
- Yolo schedules waves of at most three tasks with satisfied dependencies and isolated repositories/write sets; collisions serialize.
- The delivery/close-out of `005_closing` is mechanical/idempotent and external delivery ends at a human-merged `develop` → `main` PR.

## Invariants

- Planner never executes; reviewer never implements, integrates, or plans.
- The reviewer never dispatches the correction of what it rejected: it names the delta and the orchestrator relaunches. A gate that commissions its own fix stops being a gate.
- An approved front is never re-executed or re-integrated because another front was returned.
- Each role reads only its slice: a front's executor receives the card's request, the plan's objective/strategy, and its own front file — never the whole plan nor other fronts.
- Every complex front declares `owns`, `may_read`, `must_not_edit`, `depends_on`, expected input, skill, and criterion.
- Missing dependencies are blocked, never implemented opportunistically.
- Minimal telemetry records contexts, return counters, strategy/tests, duration, and result—never chain-of-thought.
- A live claim protects the entire task folder; front ownership protects parallel workers.

## Errors and conformance

- Return three on the same route (plan or execution) sets `circuit_breaker: true` and `blocked: true`; only explicit human reset clears that gate.
- A return without a delta or without a classification is refused: `pop_move` rejects the `005_closing→002` route without `--return-kind`, since without the type there is no way to decide between amendment and replanning.
- [x] Whoever judges act 1 — the single reviewer in B, the advocate + judge pair in A — compares objective/specs with diff, tests, and quality, and separates plan defect from execution failure; returns carry a classified delta, re-entry is partial, and re-review is differential over the delta.
- [x] `pop_yolo.py`, `pop_move.py`, `pop_status.py`, and `test_yolo_flow.py` enforce scheduler, circuit, telemetry, and delivery behavior.
- [x] [[.agents/skills/advance-task/SKILL|advance-task]], [[.agents/skills/yolo-critic/SKILL|yolo-critic]], [[.agents/skills/devils-advocate/SKILL|devils-advocate]] and [[.agents/skills/adversarial-judge/SKILL|adversarial-judge]] define role boundaries; the act-1 trigger, powers and artifact caps live in [[specs/adversarial-gate|adversarial gate]].
