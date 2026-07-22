---
name: advance-task
description: Orchestrates a task through kanban 001→006, delegating each stage to the proper fresh context and continuing until a legitimate human gate.
---

# advance-task

You are the **orchestrator**. Find the current stage, resolve gates and transitions, and continue until the next legitimate human gate. [[WORKFLOW|WORKFLOW]] is authoritative: read the current stage and transversal rules, not the whole vault.

**Delegate:** 002 and 005 always use fresh contexts. A cohesive 004 front goes directly to one executor; only a DAG, several skills, or disjoint write sets justify a sub-orchestrator. The main agent owns 001, 006, gates, and transitions.

## Loop

1. Claim first with `scripts/pop_claim.py <task-id>`. A live claim by another agent means read-only: report and stop.
2. Read `stage`, `critical`, `yolo`, `size`, `blocked`, `depends_on`, and stage skills. In 001, release and stop without `- [x] Ready to plan`, unless an explicit human command or a yolo roadmap mark authorizes it; record that source.
3. While no legitimate stop exists, run the current [[WORKFLOW|WORKFLOW]] stage. Use `scripts/pop_move.py <task-id> <stage> --reason "..." --context <id>` for transitions; never duplicate its log manually.
4. Release the claim only at a legitimate stop. Normal yolo returns at 003/005 automatically re-enter the loop.

Outside yolo, human gates are 001 release, 003 approval, critical 005, `(user)` work, a block, and merge. In yolo, 003 exists only for `critical: true` (fresh strong critic) and 005 is the **single quality gate**; only a technical block, `(user)` item, circuit breaker, or the final merge of the marked scope stops early.

## Yolo execution

- A non-critical yolo task transits 002 → 004 **directly**, with no approval round — yolo trusts the agent's plan. `critical: true` keeps 003 with a fresh strong session of the [[.agents/skills/yolo-critic/SKILL|yolo-critic]].
- Each 003 and 005 gate allows two automatic returns; the third failure activates `circuit_breaker` and requires human intervention.
- Use `scripts/pop_yolo.py wave` to schedule at most three tasks with satisfied dependencies and isolated repositories/write sets. Collisions serialize.
- A cohesive implementation uses one direct executor with `owns`, denies, and a criterion. Use a sub-orchestrator only for genuine topology.
- The 005 critic is always strong in a clean session and first checks whether the **original request** (the card's objective) was met — the brief is strategy, not an approved contract. It records `differential|full`, reason, surface, and tests; `full` is mandatory for critical tasks and after any return.
- 006 is mechanical/idempotent: local root PoP stays on `main`; external yolo tasks integrate into `develop`, then the **marked scope** (single task, phase/epoch or modification) opens `develop` → `main` without agent merge.

## Turn discipline

- Independent tasks in a wave may run concurrently, but no task transitions before its stage result is collected.
- Never end the turn with a stage agent running or with agent-owned future work merely promised.
- After collecting a wave, persist transitions and launch the next eligible wave until a legitimate stop.

## Stage contexts

- **002 planner:** card + linked research/specs → concise objective, strategy, fronts, dependencies, risks, and criteria; no implementation or chain-of-thought.
- **004 executor:** direct for one cohesive front; complex topology gets explicit `owns`, `may_read`, `must_not_edit`, dependencies, expected input, and criteria. Validate scope and the aggregate gate.
- **005 reviewer:** fresh and independent; in yolo always strong. First checks whether the original request was met, then compares objective/specs to behavior and classifies evidence-backed findings.
- **003 yolo critic (only `critical: true`):** strong, fresh, objective approval/return. Returns 1–2 loop; failure 3 opens the circuit.

Record minimal telemetry per stage: contexts, return count, verification strategy/tests, duration, and result. Never persist prompts, reasoning, or discarded attempts. Missing dependencies, scope violations, or changed contracts return/block; never fill another front opportunistically.
