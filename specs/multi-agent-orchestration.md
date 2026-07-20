# Spec — Multi-agent kanban orchestration

- **Status:** implemented
- **Created:** 2026-07-20
- **Updated:** 2026-07-20

## Contract

Planning, execution and review use distinct contexts. The kanban persists a brief sufficient for capable agents; heavy reasoning, operational prompts and discarded attempts remain ephemeral.

## Expected behavior

- 002 always uses a separate planner and records objective, strategy, fronts, dependencies, contracts, material risks and criteria.
- 004 chooses one executor, sequential specialists or parallel waves according to skills, DAG and write sets.
- Parallel fronts use isolated branches/worktrees; only the orchestrator integrates them.
- 005 uses exactly one independent reviewer per round for behavior and quality; `critical` changes depth/model.
- In yolo, the same role judges 003 and 005 in separate fresh sessions; the orchestrator performs 006 integration.

## Invariants

- The planner never executes its plan; the reviewer is never an executor.
- Parallelism requires logical and write independence.
- Every front declares `owns`, `may_read`, `must_not_edit`, `depends_on`, expected input, skill and completion criterion.
- Missing/incompatible dependencies are `BLOCKED`; consumers never implement them autonomously.
- Specialists never integrate peers; the orchestrator validates ownership before integration.
- Plans, fronts and specs contain no chain-of-thought, pseudocode or contingent micro-edits.

## Interfaces

- **Persisted brief:** [[_templates/TASK-PLAN|TASK-PLAN]] — *follow for the planner-to-execution contract*.
- **Optional front:** [[_templates/SUBTASKS|SUBTASKS]] — *follow when ownership or a gate warrants persisted tracking*.
- **Worker contract:** the same front fields, supplied ephemerally in the prompt.
- **Ownership gate:** [[scripts/pop_check_scope.py|pop_check_scope]] — *run with `--allow <owns> --deny <must_not_edit>` before integration; exit 0 allows, 1 rejects, 2 is invalid use*.
- **Review:** [[_templates/TASK-VERIFY|TASK-VERIFY]] — *follow for criteria, quality, severity and verdict*.

## Errors and limits

- Overlapping write sets → serialize fronts or redefine ownership.
- Unstable shared contract → run the producer before consumers.
- Diff outside `owns` → return it even when functionally correct.
- Integration conflict → `blocked: true`; no worker resolves a peer's branch.
- Small recon → do directly; delegate only above rule 18's floor.

## Conformance criteria

- [x] Planner, execution and review use distinct contexts.
- [x] Briefs/fronts describe decisions and contracts without microimplementation.
- [x] WORKFLOW defines DAG, ownership, isolation and centralized integration.
- [x] The automated gate covers committed, local and untracked changes.
- [x] One reviewer compares objective/specs with diff, tests and quality.

## Related references

- [[WORKFLOW|WORKFLOW]] — *follow to operate the state machine and gates*.
- [[notes/decisions/2026-07-20-harness-decisions|2026-07-20 decision]] — *follow for the rationale behind replacing prescriptive wargaming*.
