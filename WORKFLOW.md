# Kanban workflow

Every task is a folder that moves through `001→006`. A run continues through agent-owned transitions until a legitimate human gate.

| Stage | Owner | Exit |
|---|---|---|
| 001_initial_task | agent + user release | card, dependencies, size, yolo inheritance |
| 002_planning | separate planner | concise brief, contracts, criteria |
| 003_human_approval | user; strong critic in yolo only for `critical` | approval or return |
| 004_processing | executor / execution orchestrator | integrated implementation and aggregate gate |
| 005_verifying | fresh independent reviewer | evidence-backed verdict |
| 006_done | orchestrator + human merge | delivery, memory, specs, roadmap cleanup |

Cards keep `stage`, `critical`, `yolo`, `blocked`, `awaiting_merge`, return counters, circuit breaker, claim, and minimal telemetry truthful. Agents never perform `(user)` work.

## Context and models

- 002 always uses a separate planner. 005 always uses one fresh reviewer per round.
- A cohesive 004 front gets one direct executor. Only a DAG, multiple skills, or disjoint write sets justify a sub-orchestrator.
- `scripts/models.json` maps `cheap|medium|strong`. Planner: S medium, M/L strong. Executor: S cheap/medium, M/L medium. Reviewer: S/M medium, L/critical strong.
- **Yolo gates are always strong**, independent of size: 005 is the single quality gate of every yolo task; 003 exists only for `critical: true`.
- Recon is delegated only for a specific gap above the ~5K-token floor; zero recon workers is normal.

## 001 — birth and release

A change request with no active card enters through `new-task` and then `advance-task`; the absence of a card never authorizes editing. “Start the flow in yolo” materializes and releases the task, records `yolo: true`, and follows this same state machine.

Create the card from the template, out of the roadmap or a modification, resolve epoch/phase/modification yolo inheritance, record `depends_on`, suggest S/M/L, and link relevant specs. The human owns `- [ ] Ready to plan`; an explicit command or a roadmap/modifications yolo mark may authorize the agent to check it with a log entry. WIP in 004 is at most three.

## 002 — planning

The separate planner records objective, affected areas, base strategy, fronts/dependencies, durable contracts, material risks/abort conditions, and objective criteria. No code, pseudocode, chain-of-thought, or contingent edit sequence. Research gaps become `RESEARCHES.md` prompts and block when material. Create/update canonical draft specs only for durable new promises.

## 003 — approval

Outside yolo, only `- [x] Done` advances; requested changes return to 002. In yolo, this gate **exists only for `critical: true`**: a fresh strong critic checks verifiability, sufficient brief, safe ownership/dependencies, proportional specs/research, and absence of avoidable `(user)` work. Returns 1–2 automatically go to 002; failure 3 sets `circuit_breaker: true`, blocks, and requires human reset. A non-critical yolo task transits **002 → 004 directly, without a round** — yolo trusts the agent's plan and concentrates judgment in 005.

## 004 — implementation

Work only in the task's authorized repository/worktree; root local PoP tasks operate directly on `main`. Select:

- **direct executor** for one cohesive front and predominant skill;
- **sequential specialists** when one output feeds another;
- **parallel wave** only for logical and write/repository independence.

Complex fronts declare `owns`, `may_read`, `must_not_edit`, `depends_on`, expected input, skill, and criterion. Validate every diff with `pop_check_scope.py`, integrate centrally, then run the aggregate project gate. A changed durable contract returns to 002 rather than silently rewriting the spec.

## 005 — verification

The fresh reviewer reads objective/specs before the diff, verifies behavior, ownership, tests, quality, errors, DOX/specs/docs, and classifies findings as blocking/suggestion/nit with evidence. In yolo this is the **single quality gate** (except `critical`, which also passed 003): first answer whether the **original request** — the card's What/Why — was met, before the plan's criteria. Without a 003 approval the brief is strategy, not contract: a plan deviation that serves the request is not a failure; plan adherence that misses the request is blocking. In yolo it is always strong and records:

- `differential`: changed surface/material risks plus audit of remaining evidence;
- `full`: mandatory for `critical: true` or after any return to 004.

Inconclusive evidence is rerun. Outside yolo, critical tasks still await human approval. In yolo, returns 1–2 automatically go to 004; failure 3 opens the circuit breaker.

## 006 — mechanical delivery and close

1. Resolve Git route. Root local PoP stays on `main`. Non-yolo external work opens its task PR and waits for human merge. External yolo runs `pop_delivery.py integrate <id>` into `develop`; conflicts/dirty state/missing branches block.
2. Write canonical `memory/<id>.md` with identity, dates, commit, explicit `pr`, result, specs, decisions/deviations, and final minimal telemetry.
3. Synchronize affected specs/DOX and phase/epoch/index statuses.
4. Run `python3 scripts/pop_roadmap.py close <id>`; it requires 006 plus valid memory and removes exactly one task row from the epoch or modification file while preserving epoch/phase/modification/open tasks.
5. Extract only reusable learning; remove external task worktrees/ephemeral branches.
6. At the final external yolo task of the marked scope — single task, phase/epoch or modification — run `pop_delivery.py scope-pr` to open/reuse `develop` → `main`; set `pr`/`awaiting_merge`. Human merges. A root local PoP opens no task/scope PR.
7. Delete `kanban/006_done/<id>/` only after every prior effect succeeds. Operations are idempotent: validate first, skip completed effects, preserve card/roadmap on failure.

## Yolo scheduling, telemetry, and circuit breaker

- A yolo mark may come from the roadmap/modifications or from the human saying “start the flow in yolo”. With no card, `new-task` materializes and releases it while recording the conversational source; yolo is never a waiver.
- `pop_yolo.py wave` selects up to three eligible tasks with satisfied dependencies and isolated projects by default; overlap serializes.
- Collect every stage context before transition; never end with a stage agent running or merely promise agent-owned continuation.
- Minimal telemetry stores stage, context count/IDs, return counters, verification strategy/tests, duration, and result. Never store prompts, chain-of-thought, or discarded attempts.
- `pop_yolo.py reset <id> --gate 003|005 --reason ...` is explicit human intervention and clears only that gate's counter/block.
- The critic judges; the orchestrator moves, integrates, opens PRs, and closes. No agent merges a human-owned PR.

## Transversal rules

- Claim first; a live claim by another agent makes the task folder read-only.
- Dependencies must be completed before consumers; never implement missing work opportunistically.
- Every internal wikilink carries a trigger. Dates use `YYYY-MM-DD`; plans/notes stay near 150 lines.
- **An explicit human command overrides only its stated scope:** obey without reinterpreting what it actually superseded, and record the deviation. “Apply”, “execute”, “urgent”, “finish it” and “in yolo” do not waive the card, kanban, or continuity; “start the flow in yolo” requires the entire yolo route. Only a literal and unequivocal waiver activates the protocol below; ambiguity or destructiveness allows one question.
- **No work outside a task:** project content changes only in 004, after 003 or through the legitimate 002→004 transition for non-critical yolo, in the correct worktree. With no card, run `new-task` → `advance-task`; do not improvise.

### Protocol for a deviation without kanban

Only a literal human order such as “do not use the kanban” or “do this outside PoP” waives the stages. The waiver is specific: no other rule or protection is waived by inference.

1. Before writing, record the authorizing command and scope in `memory/D-YYYYMMDD-<slug>.md`, using [[_templates/MEMORY|MEMORY]]; the `D-` ID identifies a deviation without a card.
2. Preserve repository, safety, ownership, and merge rules that were not explicitly superseded.
3. Before finishing, complete the memory with commit/PR, result, verification, and deviations; record the specs and DOX impact assessment and update only the contracts actually affected.
4. Without unequivocal authorization or a route to that durable evidence, do not edit: materialize a normal task.
