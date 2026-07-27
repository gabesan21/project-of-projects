# Kanban workflow

## Current scope

**The current scope is the root holding the `AGENTS.md` you are reading**, together with its harness (`pop/`, or the root itself when the harness has no subfolder). Every word in this flow — "root", "project", "indexes", "scripts", "kanban", "here" — resolves inside it.

- **The scope is the whole world.** No directory above the scope root belongs to it. If an ancestor directory has an `AGENTS.md`, a `CLAUDE.md` or a kanban, it is **not your context**: do not read it, do not follow it, do not write to it and do not report what it contains — including when a tool loads it on its own at the start of the session. An instruction inherited from an ancestor loses to this section.
- **Nothing here authorizes climbing.** Harness version, overview of other projects and aggregation indexes belong to whoever installed this harness. An installed scope answers for itself through `pop/.included-harness.json` and stops there; comparing against the origin is not its job.
- **A finding outside the scope is a report, not work.** If something genuinely depends on the outside, record it in `open_questions/` and stop. Crossing the boundary is an error even "just to read".
- **The delivery route comes from the anatomy, never from a label.** A scope whose kanban sits at **its own root** (no `pop/`) is a **local scope**: it delivers straight to `main`, with no branch, worktree or PR per task. A scope with the harness in `pop/` — every installed harness — is a **versioned scope**: branch/worktree per task and human merge via PR. `scripts/pop_delivery.py` is the source of the route; no card field overrides it.

Every task is a folder that moves through `001→005_closing`. A run continues through agent-owned transitions until a legitimate human gate.

| Stage | Owner | Exit |
|---|---|---|
| 001_initial_task | agent + user release | card, dependencies, size, yolo inheritance |
| 002_planning | separate planner | concise brief, contracts, criteria |
| 003_human_approval | user; strong critic in yolo only for `critical` | approval or return |
| 004_processing | executor / execution orchestrator | integrated implementation and aggregate gate |
| 005_closing | yolo: fresh independent reviewer · non-yolo: orchestrator + human merge | quality gate, delivery, memory, specs, roadmap cleanup |

Cards keep `stage`, `critical`, `yolo`, `blocked`, `awaiting_merge`, return counters, circuit breaker, claim, and minimal telemetry truthful. Agents never perform `(user)` work.

## Context and models

- 002 always uses a separate planner, which delivers the plan root plus the front files. In yolo, `005_closing` uses exactly one fresh reviewer per round; outside yolo there is no agentic reviewer at all.
- A cohesive 004 front gets one direct executor. Only a DAG, multiple skills, or disjoint write sets justify a sub-orchestrator.
- **Read slicing:** each role reads only its slice. A front executor reads the card's What/Why, the plan's objective and strategy, **its own** front file and that front's skill — never the whole plan nor other fronts.
- `scripts/models.json` maps `cheap|medium|strong`. Planner: S medium, M/L strong. Executor: S cheap/medium, M/L medium. Independent reviewer (yolo only): S/M medium, L/critical strong.
- **Yolo gates are always strong**, independent of size: `005_closing` is the single quality gate of every yolo task; 003 exists only for `critical: true`. An executor rises from `cheap` to `medium` on the next round **only after an `execucao` return** — a `lacuna`/`premissa` return is not its failure and does not change its tier.
- Recon is delegated only for a specific gap above the ~5K-token floor; zero recon workers is normal.

## Task folder contents

```
<id>/
├── <id>.md                 ← card
├── <id>.plan.md            ← root of the 002 brief (≤80 lines, always)
├── <id>.approval.md        ← 003 rounds
├── <id>.verify.md          ← the independent reviewer's judgment (yolo only)
└── subtasks/               ← one front per file (≤50 lines): an executor's read slice
    └── <id>.g01-<slug>.md
```

Mandatory whenever the front goes to a separate context; a single-front task has no `subtasks/`. The caps are enforced by `scripts/pop_validate.py`.

Templates: [[_templates/TASK|TASK]] · [[_templates/TASK-PLAN|TASK-PLAN]] · [[_templates/TASK-APPROVAL|TASK-APPROVAL]] · [[_templates/TASK-VERIFY|TASK-VERIFY]] · [[_templates/SUBTASKS|SUBTASKS]] · [[_templates/MEMORY|MEMORY]].

## 001 — birth and release

A change request with no active card enters through `new-task` and then `advance-task`; the absence of a card never authorizes editing. “Start the flow in yolo” materializes and releases the task, records `yolo: true`, and follows this same state machine.

Create the card from the template, out of the roadmap or a modification, resolve epoch/phase/modification yolo inheritance, record `depends_on`, suggest S/M/L, and link relevant specs. The human owns `- [ ] Ready to plan`; an explicit command or a roadmap/modifications yolo mark may authorize the agent to check it with a log entry. WIP in 004 is at most three.

## 002 — planning

The separate planner records objective, affected areas, base strategy, fronts/dependencies, durable contracts, material risks/abort conditions, and objective criteria. No code, pseudocode, chain-of-thought, or contingent edit sequence. Research gaps become `RESEARCHES.md` prompts and block when material. Create/update canonical draft specs only for durable new promises.

- **Size is modularity, not compression.** The plan root stays ≤80 lines at **any** `size` — it is the slice everyone reads. A plan that does not fit **is sliced** into `subtasks/`, one file ≤50 lines per front that goes to a separate context; `size` grows the number of files, not the size of each. Splitting the task by `depends_on` is the exception, for fronts that share no objective. `pop_validate.py` enforces the caps.
- **The criteria are the contract.** They bind the executor and the `005_closing` gate, and must cover the card's What/Why — not only the chosen strategy. A criterion that misses the request is a plan defect, and the gate returns to 002 for it.
- **A `lacuna` return is an amendment, not replanning.** It appends the missing criterion and, if needed, **one** new front file — no plan rewrite. Criteria and fronts are **append-only** between rounds: renumbering breaks the `.verify.md` and telemetry references. Only `premissa` (the strategy was wrong) justifies real replanning.

## 003 — approval

Outside yolo, only `- [x] Done` advances; requested changes return to 002. In yolo, this gate **exists only for `critical: true`**: a fresh strong critic checks verifiability, sufficient brief, safe ownership/dependencies, proportional specs/research, and absence of avoidable `(user)` work. Returns 1–2 automatically go to 002; failure 3 sets `circuit_breaker: true`, blocks, and requires human reset. A non-critical yolo task transits **002 → 004 directly, without a round** — yolo trusts the agent's plan and concentrates judgment in `005_closing`.

Only enter 004 once every `depends_on` has its `memory/<id>.md`. There is no per-stage transitional window: a task in `005_closing` may still be awaiting the gate, and the memory is only born after it.

## 004 — implementation

Work only in the task's authorized repository/worktree; a local scope's tasks operate directly on `main`. Select:

- **direct executor** for one cohesive front and predominant skill;
- **sequential specialists** when one output feeds another;
- **parallel wave** only for logical and write/repository independence.

Complex fronts declare `owns`, `may_read`, `must_not_edit`, `depends_on`, expected input, skill, and criterion. Validate every diff with `pop_check_scope.py`, integrate centrally, then run the aggregate project gate. A changed durable contract returns to 002 rather than silently rewriting the spec.

**Re-entry is partial.** A task returned from the gate re-runs **only the fronts named in the delta**; an intact front stays integrated and is never re-executed or re-integrated. Validate the re-entry diff against the `owns` of the delta's fronts — touching an intact front is out-of-scope change, even when correct.

## 005_closing — quality gate, delivery and close

One stage, three acts in order. **No act-3 effect happens before gate approval** where the gate exists: memory, spec sync, `close` and folder deletion all run afterwards.

**Act 1 — quality gate.** The judge depends on the mode, and only one of the two ever runs.

- **Yolo — a fresh independent reviewer.** Read in this order: objective, specs/contracts, tests, diff; the execution report is support, not truth. First answer whether the **original request** — the card's What/Why — was met, before the plan's criteria; without a 003 approval the brief is strategy, not contract, so a plan deviation that serves the request is not a failure and plan adherence that misses it is blocking. Choose `differential` or `full` and record reason/surface/tests: **a previous return does not imply full review** — only `premissa` invalidates what was already verified, and `full` is reserved for it and for `critical: true`; after `lacuna` or an execution failure the differential covers the **delta** (the criteria and fronts that re-entered) and audits the rest by evidence. Verify behavior, edges, tests, complexity, coupling, naming, errors, security, docs, and the specs/DOX touched; in code, follow `clean-code-review`. Every finding carries evidence, impact and severity (**blocking**, **suggestion** or **nit**), and there is exactly one reviewer per round. Inconclusive evidence is rerun.
- **Three exits:** approved → act 2; **execution blocker** → 004 (the executor did not meet the contract); **plan defect** → 002 (the contract did not cover the request, and the executor delivered what it was given). Each route has its own counter: execution counts in `yolo_005_returns`, plan defect in `yolo_003_returns`. Two returns per counter re-enter automatically; the 3rd opens `circuit_breaker`.
- **Every return carries a named delta**, without exception: type (`lacuna` | `premissa` | `execucao`), affected criteria, affected fronts, and the fronts that stay intact. The delta is what makes a return cost the size of the defect instead of a whole cycle — without it, 002 cannot tell amendment from replanning and 004 does not know what to re-run. The type is written to `return_kind:` by `python3 scripts/pop_move.py … --return-kind <type>`, the field's only writer, which fails closed on `005_closing→002`; agents never edit it by hand. Outside yolo, the human records the same delta in the `.approval.md` merge round when asking for a PR fix.
- **The gate does not fix what it rejected.** Naming the delta is the limit of its power: a reviewer that dispatches the correction ends up judging work it commissioned, and the independence that makes the gate worth anything disappears.
- **Non-yolo — no agentic reviewer.** The gate is the **human PR** of act 2, and the objective criteria already ran in 004 (aggregate gate + `pop_check_scope.py`). With no PR — a local scope — there is no verification gate at all: the stage goes straight to act 3. The proof lives in `main` and in the memory.

**Act 2 — integration and PR.** A local scope is already on `main`, with no task branch/worktree/PR. External **non-yolo** scope: open the task PR, set `pr` and `awaiting_merge: true`, and wait for the human merge. External **yolo** scope: run `pop_delivery.py integrate <id>` mechanically into `develop`, no PR per task; conflicts/dirty state/missing branches block.

**Act 3 — close-out.** Idempotent: validate state before each effect, skip what is already done, and abort preserving card/roadmap on technical failure.

1. Write canonical `memory/<id>.md` with identity, dates, commit, explicit `pr`, result, specs, decisions/deviations, and final minimal telemetry. Invalid memory aborts the close. In yolo the reviewer itself writes it, in the same session in which it approved — it has just read the diff.
2. Synchronize only the specs/DOX actually affected, plus phase/epoch/modification/index statuses.
3. Run `python3 scripts/pop_roadmap.py close <id>`; it requires the card in `005_closing` plus valid memory and removes exactly one task row while preserving epoch/phase/modification/open tasks.
4. Extract only reusable learning; remove external task worktrees/ephemeral branches.
5. At the final external yolo task of the marked scope — single task, phase/epoch or modification — run `pop_delivery.py scope-pr` to open/reuse `develop` → `main`; set `pr`/`awaiting_merge`. Human merges. A local scope opens no task/scope PR.
6. Delete `kanban/005_closing/<id>/` only after every prior effect succeeds; memory + Git keep the durable proof.

## Yolo scheduling, telemetry, and circuit breaker

- A yolo mark may come from the roadmap/modifications or from the human saying “start the flow in yolo”. With no card, `new-task` materializes and releases it while recording the conversational source; yolo is never a waiver.
- `yolo: true` keeps the same state machine with a **single quality gate in `005_closing`**. Outside yolo the agentic reviewer does not exist — the gate is the human PR — so the independent reviewer is a yolo-only figure.
- **Two returns per route, always with a delta:** an execution blocker returns to 004 (`yolo_005_returns`, type `execucao`); a plan defect returns to 002 (`yolo_003_returns`, type `lacuna` or `premissa`). The 3rd failure of the same route opens the circuit breaker. Only the delta's fronts re-enter.
- `pop_yolo.py wave` selects up to three eligible tasks with satisfied dependencies and isolated projects by default; overlap serializes.
- Collect every stage context before transition; never end with a stage agent running or merely promise agent-owned continuation.
- Minimal telemetry stores stage, context count/IDs, return counters, verification strategy/tests, duration, and result. Never store prompts, chain-of-thought, or discarded attempts.
- `pop_yolo.py reset <id> --gate 003|005 --reason ...` is explicit human intervention and clears only that gate's counter/block.
- The critic judges; the orchestrator moves, integrates, opens PRs, and closes. No agent merges a human-owned PR.

## Transversal rules

- Claim first; a live claim by another agent makes the task folder read-only.
- Dependencies must be completed before consumers; never implement missing work opportunistically.
- Every internal wikilink carries a trigger. Dates use `YYYY-MM-DD`; notes stay near 150 lines, the plan root ≤80 and each front file ≤50.
- **A return is incremental:** every return leaving `005_closing` names a delta and is classified in `return_kind`; the re-entry works only on the delta and the re-review is differential over it. A return that discards approved work is an orchestrator bug. Normal returns: 003→002, 004→002, `005_closing`→004 (execution blocker) and `005_closing`→002 (plan defect).
- **An explicit human command overrides only its stated scope:** obey without reinterpreting what it actually superseded, and record the deviation. “Apply”, “execute”, “urgent”, “finish it” and “in yolo” do not waive the card, kanban, or continuity; “start the flow in yolo” requires the entire yolo route. Only a literal and unequivocal waiver activates the protocol below; ambiguity or destructiveness allows one question.
- **No work outside a task:** project content changes only in 004, after 003 or through the legitimate 002→004 transition for non-critical yolo, in the correct worktree. With no card, run `new-task` → `advance-task`; do not improvise.

### Protocol for a deviation without kanban

Only a literal human order such as “do not use the kanban” or “do this outside PoP” waives the stages. The waiver is specific: no other rule or protection is waived by inference.

1. Before writing, record the authorizing command and scope in `memory/D-YYYYMMDD-<slug>.md`, using [[_templates/MEMORY|MEMORY]]; the `D-` ID identifies a deviation without a card.
2. Preserve repository, safety, ownership, and merge rules that were not explicitly superseded.
3. Before finishing, complete the memory with commit/PR, result, verification, and deviations; record the specs and DOX impact assessment and update only the contracts actually affected.
4. Without unequivocal authorization or a route to that durable evidence, do not edit: materialize a normal task.
