---
id: multi-agent-orchestration
project: pop
domain: harness
kind: contract
status: active
implementation: implemented
origin: "4.2"
created: 2026-07-20
updated: 2026-07-21
supersedes: []
superseded_by:
---

# Spec — Multi-agent kanban orchestration

## Contract

Planning, execution, and review use distinct contexts. Cards persist a sufficient brief and minimal telemetry; heavy reasoning, prompts, and discarded attempts remain ephemeral.

## Expected behavior

- 002 always uses a separate planner; 005 always uses one fresh independent reviewer per round.
- A cohesive 004 front receives a direct executor. DAGs, multiple skills, or disjoint write sets receive a sub-orchestrator with explicit contracts.
- Yolo 003 and 005 always use strong fresh critics. Each gate permits two automatic returns; failure three opens a circuit breaker requiring human intervention.
- 005 chooses `differential|full`; full is mandatory for critical tasks or after a return.
- Yolo schedules waves of at most three tasks with satisfied dependencies and isolated repositories/write sets; collisions serialize.
- 006 effects are mechanical/idempotent and external delivery ends at a human-merged `develop` → `main` PR.

## Invariants

- Planner never executes; reviewer never implements or integrates.
- Every complex front declares `owns`, `may_read`, `must_not_edit`, `depends_on`, expected input, skill, and criterion.
- Missing dependencies are blocked, never implemented opportunistically.
- Minimal telemetry records contexts, return counters, strategy/tests, duration, and result—never chain-of-thought.
- A live claim protects the entire task folder; front ownership protects parallel workers.

## Errors and conformance

- Return three at 003/005 sets `circuit_breaker: true` and `blocked: true`; only explicit human reset clears that gate.
- [x] `pop_yolo.py`, `pop_move.py`, `pop_status.py`, and `test_yolo_flow.py` enforce scheduler, circuit, telemetry, and delivery behavior.
- [x] [[.agents/skills/advance-task/SKILL|advance-task]] and [[.agents/skills/yolo-critic/SKILL|yolo-critic]] define role boundaries.
