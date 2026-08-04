---
name: advance-task
description: Orchestrates a task through kanban 001→005_closing, delegating each stage to the proper fresh context and continuing until a legitimate human gate.
---

# advance-task

You are the **orchestrator**. Find the current stage, resolve gates and transitions, and continue until the next legitimate human gate. [[WORKFLOW|WORKFLOW]] is authoritative: read the current stage and transversal rules, not the whole scope.

**Delegate:** 002 always uses a fresh context, and so does the `005_closing` gate **in yolo** — the Judge Dredd, single judge. A cohesive 004 front goes directly to one executor; only a DAG, several skills, or disjoint write sets justify a sub-orchestrator. The main agent owns 001, the gates, the transitions, and the whole of `005_closing` outside yolo — there is no agentic reviewer there.

## Input

- **Task id:** locate the task folder in the project's kanban.
- **Change request with no id/card:** apply the **rule-13 triage** first — a direct fix (evident scope, no new contract, no planning, one session) follows the "Direct fix" section of [[WORKFLOW|WORKFLOW]] and does not enter the kanban; everything else runs `new-task` with the context the human already provided, then resumes this loop. If the human said “start the flow in yolo”, materialize/release with `yolo: true` and follow the entire route.

## Loop

1. Claim first with `scripts/pop_claim.py <task-id>`. A live claim by another agent means read-only: report and stop.
2. Read `stage`, `critical`, `yolo`, `size`, `blocked`, `depends_on`, and stage skills. In 001, release and stop without `- [x] Ready to plan`, unless an explicit human command or a yolo roadmap mark authorizes it; record that source.
3. While no legitimate stop exists, run the current [[WORKFLOW|WORKFLOW]] stage — **001** and the delivery/close-out of `005_closing` yourself (they are cheap); **002/004** and the yolo `005_closing` gate through a dedicated subagent. Use `scripts/pop_move.py <task-id> <stage> --reason "..." --context <id>` for transitions; never duplicate its log manually. A return leaving `005_closing` carries `--return-kind lacuna|premissa` (→002) or omits the flag (→004, `execucao`), recording the cause in the card and the telemetry.
4. Release the claim only at a legitimate stop. Normal yolo returns automatically re-enter the loop.

Outside yolo, human gates are 001 release, 003 approval, `(user)` work, a block, and the **PR merge — which is the verification**. Never open an agentic reviewer outside yolo: with no PR (root-local PoP) the quality gate does not exist and `005_closing` goes straight to close-out. In yolo, 003 exists only for `critical: true` (fresh strong Judge Dredd) and the `005_closing` gate is the **single quality gate**; only a technical block, `(user)` item, circuit breaker, or the final merge of the marked scope stops early.

`005_closing` is **one stage with three acts, in order**: quality gate, delivery/PR, close-out (memory, spec sync, `pop_roadmap close`, folder deletion). No close-out effect happens before the gate approves.

## Yolo execution

- A non-critical yolo task transits 002 → 004 **directly**, with no approval round — yolo trusts the agent's plan. `critical: true` keeps 003 with a fresh strong session of the [[.agents/skills/judge-dredd/SKILL|judge-dredd]].
- Two automatic returns per route; the third failure of the **same** route activates `circuit_breaker` and requires human intervention (`yolo_003_returns` for plan, `yolo_005_returns` for execution).
- Use `scripts/pop_yolo.py wave` to schedule at most three tasks with satisfied dependencies and isolated repositories/write sets. Collisions serialize.
- A cohesive implementation uses one direct executor with `owns`, denies, and a criterion. Use a sub-orchestrator only for genuine topology.
- The `005_closing` judge runs in a clean session at the matrix tier (medium in `S`/`M`, strong in `L`/`critical`) and first checks whether the **original request** (the card's objective) was met — the brief is strategy, not an approved contract. It records `differential|full`, reason and surface; `full` is mandatory for critical tasks and after a `premissa` return (`scripts/pop_yolo.py verify-mode <id>` computes it from `return_kind`).
- The gate has **three exits**: approved; execution blocker → 004 (`yolo_005_returns`, kind `execucao`); plan defect → 002 (`yolo_003_returns`, kind `lacuna` or `premissa`), when the plan's criteria did not cover the card's request and the executor delivered the slice it was given. Every return names a **delta** — type, affected criteria, fronts re-entering, fronts staying intact.
- Delivery/close-out is mechanical and idempotent: a local scope stays on `main`; external yolo tasks integrate into `develop`, then the **marked scope** (single task, phase/epoch or modification) opens `develop` → `main` without agent merge.

## Turn discipline

- Independent tasks in a wave may run concurrently, but no task transitions before its stage result is collected.
- Never end the turn with a stage agent running or with agent-owned future work merely promised.
- After collecting a wave, persist transitions and launch the next eligible wave until a legitimate stop.

## Stage contexts

- **002 planner:** card + linked research/specs → the plan root (**≤80 lines at any `size`**) with objective, strategy, fronts, dependencies, risks, and criteria, **plus one file in `subtasks/` (≤50 lines) per front that goes to a separate context**; no implementation or chain-of-thought. A plan that doesn't fit **modularizes**, it doesn't compress.
- **004 executor:** direct for one cohesive front; complex topology gets explicit `owns`, `may_read`, `must_not_edit`, dependencies, expected input, and criteria. Validate scope and the aggregate gate. **Hand over the slice, not the plan:** each executor gets the card's What/Why, the objective and strategy, **its own** front file and that front's skill — never the whole plan nor other fronts.
- **004 on re-entry:** relaunch **only** the fronts in the `.verify.md` delta (outside yolo, the `.approval.md`), with the delta in the prompt. A front listed as intact is approved: don't relaunch it, don't re-integrate it, and treat a diff in it as out of scope.
- **`005_closing` gate (yolo only):** launch the **Judge Dredd** ([[.agents/skills/judge-dredd/SKILL|judge-dredd]]) in a clean session at the matrix tier (medium in `S`/`M`, strong in `L`/`critical`) — one judge per round, for every yolo task; the gate itself lives in [[WORKFLOW|WORKFLOW]]. He chooses `differential|full` (`full` for critical or a `premissa` return; otherwise differential over the delta — `pop_yolo.py verify-mode <id>` computes it), records reason/surface and starts from the original request; he judges by reading, **without re-running criteria or executing tests** (testing belongs to the `phase-verification` task). Returning, he fills in the delta; approving, he writes the memory in that same session. He **never** dispatches the fix — integration, PR, and merge stay yours. A **directed repair** verdict (pinpoint delta): **you** dispatch a medium executor with only the delta, hand the patch back to the same judge for the round's ≤10-line addendum, and record it in the Log — no `pop_move`, no counter (max 2 per round; the 3rd becomes a route).
- **003 yolo (only `critical: true`):** the strong Judge Dredd signs or returns with objective reasons. Returns 1–2 of each route loop automatically; the third of the same route opens the circuit.

Record minimal telemetry per stage: contexts, return count, verification strategy/tests, duration, and result. Never persist prompts, reasoning, or discarded attempts. Missing dependencies, scope violations, or changed contracts return/block; never fill another front opportunistically.

Never skip stages or gates. Allowed returns: 003→002, 004→002, `005_closing`→004 (execution blocker) and `005_closing`→002 (plan defect) — the orchestrator decides the return; the subagent only reports. **Yolo exception:** a non-critical yolo task transits 002 → 004 directly — that is the flow, not a skip. A learning at close-out **updates the existing note on the same theme** when there is one (don't duplicate); a contradiction with a previous note/decision becomes a visible `> Contradicts: [[target]] — <why>` line.

Never infer a waiver: “apply”, “execute”, “urgent”, “finish it” or “in yolo” do not waive the card, kanban, memory, specs, or DOX. Only a literal human waiver follows the WORKFLOW protocol for a deviation without kanban, and only within the named scope.
