---
name: advance-task
description: Orchestrates a task through the kanban (001→006), delegating each work stage to a dedicated subagent and chaining stages to the next human gate. Use when asked to advance, plan, execute, verify or complete a task.
---

# advance-task

You are the **orchestrator**: identify the task stage, resolve gates/transitions and advance to the next human gate. [[WORKFLOW|WORKFLOW]] is authoritative; read only the current stage and Cross-cutting rules.

**Delegate all 002, 004 and 005 work** with fresh context per stage. The kanban orchestrator performs 001, 006, gates and transitions; in 004 it delegates to an **execution orchestrator**, which chooses topology and integrates fronts.

## Input and loop

0. Claim first with `scripts/pop_claim.py <task-id>`; an active foreign claim forbids writes.
1. Read `stage`, `critical`, `yolo`, `size`, `blocked`, `depends_on` and skills. An unreleased 001 is a human gate unless explicit command or yolo release applies.
2. Until a human gate: perform 001/006 directly and 002/004/005 through dedicated subagents. `size: S` reduces brief, executor count and review depth but **never joins planner, executor and reviewer context**.
3. Transition with `scripts/pop_move.py ... --reason "short reason — contexts: <actually launched>"`.
4. At a gate release the claim, stop and report current state, human need and next action.

Human gates: 001 release; 003 approval; human approval for critical 005; `(user)` item; `blocked`; merge round in 006.

For `yolo: true`, delegate 003 and 005 judgment to the **independent reviewer** via [[.agents/skills/yolo-critic/SKILL|yolo-critic]] in separate fresh sessions. The orchestrator performs mechanical 006 integration. Human stops are `(user)`, `blocked` and final scope review. Continue the yolo scope in dependency order with WIP 3 until a stop or close-out.

## Turn discipline

- Stage delegation is synchronous: collect the 002/004/005 result before proceeding.
- Never end while a stage subagent is running or promise future agent-owned work.
- The yolo scope loop runs in the same turn until human stop, block or completed close-out.

## Stage subagents

Give each only its stage skill and minimal context, no web, an output cap and the model tier from `scripts/models.json`. Heavy reasoning, operational prompts and discarded attempts stay ephemeral.

- **002 — separate planner:** card + linked research/specs → concise `.plan.md` with objective, areas, strategy, fronts, dependencies, real risks and criteria; no code, pseudocode or micro-edits. Budgeted recon only for a concrete gap above rule 18's floor; zero workers is valid.
- **004 — execution orchestrator:** plan + minimal context → single executor, sequential specialists or parallel waves. Every ephemeral front declares `owns`, `may_read`, `must_not_edit`, `depends_on`, `expected_input`, skill and criterion. Launch only after dependencies are integrated; missing/incompatible input is `BLOCKED`, never opportunistic implementation. Parallel fronts use isolated worktrees/branches and require logical/write independence. Validate with `pop_check_scope.py --allow ... --deny ...`, integrate centrally and run the aggregate gate.
- **005 — independent reviewer:** objective/card + specs + integrated diff + criteria → `.verify.md` with evidence and findings. In fresh context and never as executor, compare implementation to objective, rerun gates and review code quality; severity `blocking | suggestion | nit`. `critical` changes tier/depth, not reviewer count. In yolo, start a fresh session even if the role judged 003.
- **003 yolo — brief reviewer:** card + plan + approval → sign or return with objective reasons; maximum two returns. It neither executes nor integrates.

## Cautions

- Never skip stages/gates. Normal returns: 003→002, 004→002, 005→004.
- A foreign claim covers the entire task folder.
- Abort, `(user)` or plan-changing discovery is reported; do not improvise in the main context.
- A front with missing dependency, out-of-owns path or incompatible contract returns to the execution orchestrator; never let it complete another front.
- Clear `blocked`/`blocked_reason` when unblocking.
- In 006, update an existing learning on the same theme rather than duplicating; make contradictions explicit.
