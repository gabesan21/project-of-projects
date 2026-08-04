---
id: judge-dredd
project: pop
domain: harness
kind: contract
status: active
implementation: implemented
origin: "D-20260804"
created: 2026-08-04
updated: 2026-08-04
supersedes: [adversarial-gate]
superseded_by:
---

# Spec — Judge Dredd (yolo's single gate) and phase verification

## Contract

In a `yolo: true` task, act 1 of `005_closing` is judged by **a single judge**: the **Judge Dredd** (skill `judge-dredd`) — accuser, jury and executioner of the sentence in one context. He **only decides whether something needs adjusting**: he judges by reading (integrated diff + recorded evidence) and names route and delta; he does not re-run criteria or execute tests. The adversarial pair (devil's advocate + judge) and the `yolo-critic` reviewer were **retired on 2026-08-04** — this contract supersedes the [[specs/adversarial-gate|adversarial gate]].

**Tests run once per phase**, in its last task (`phase-verification`), never per task — the "Phase verification" section of the [[WORKFLOW|WORKFLOW]] is the operational norm.

## Expected behavior

- Given any `yolo: true` task at act 1 of `005_closing`, **exactly one** Judge Dredd runs in a fresh context, tier per the WORKFLOW matrix (medium in `size: S`/`M`, strong in `L` or `critical: true`). `size`/`critical` change tier and depth (`differential|full`), never the number of judges.
- Given a `yolo: false` task, there is no agentic reviewer: the gate is the human PR; with no PR (local scope) there is no verification gate.
- Given a `critical: true` task, the strong Judge Dredd also judges the 003 gate (adversarial reading of the plan), in a session distinct from the 005 one.
- The judge first answers whether the card's **original request** was met; every finding passes the **materiality test** (verifiable source, nameable damage, a requested demand, not automatable, not already tracked) before entering the artifact.
- On approval, the judge writes the memory in the same session; on a return, he names the delta (`lacuna` | `premissa` | `execucao`) in the form of [[_templates/TASK-VERIFY|TASK-VERIFY]] and the orchestrator carries it with `pop_move --return-kind`.
- A plan criterion that requires executing a test is born `verify: phase` and is not judged at the task's gate: it accumulates in the phase checklist and runs in the `phase-verification` task, the only one whose plan declares a re-run as an `agent` criterion.

## Invariants

- **The judge's power:** judge, decide the exit, name the delta, write the memory on approval. **Prohibitions:** fixing what he rejected or dispatching the correction; editing the card's frontmatter; integrating, moving or deleting the folder; executing tests outside the phase's verification task.
- The judge is a context distinct from planner and executors; no judge executes the solution he judges.
- The trigger is derivable from the frontmatter alone (`yolo`, `size`, `critical`); no new mark fires the gate.
- Counters: `yolo_005_returns` (execution) and `yolo_003_returns` (plan); two returns per route, `circuit_breaker` on the 3rd — early when the delta repeats the theme with no new fact.
- **Directed repair:** a pinpoint blocker is not a route — a patch dispatched by the orchestrator, checked in a ≤10-line addendum in the same round; max 2 per round.
- **An environment failure never returns** (qualified pass + human checklist); a `verify: user` criterion is not judged by the gate.
- **The gate does not expand the scope:** a finding outside the request becomes a follow-up; `lacuna` fits once per task.
- Every return carries a classified delta; the re-entry covers only the delta and expensive evidence is reused.
- "No material finding" is a valid, successful outcome for the judge.

## Interfaces

| Artifact | Who writes it | Born in | What it carries | Cap |
|----------|---------------|---------|-----------------|-----|
| `<id>.verify.md` | Judge Dredd | `005_closing` (act 1) | original request, criteria by evidence, material findings with severity/evidence/remedy, verdict, delta on a return; one `## Round <n>` section per round, never deleting the previous one | ≤80 lines |

- **Gate input:** the card (What/Why and frontmatter), plan and criteria, linked specs and the integrated diff.
- **Retired artifacts:** `.defense.md`, `.r<n>.accusation.md` and `.r<n>.judgment.md` are not born in a card created on or after **2026-08-04**; in an older card they are tolerated history, treated as evidence.
- **Phase checklist:** the `verify: phase` criteria accumulated by the tasks are the input of the `phase-verification` task's 002 (source: memory + plans in Git).

## Errors and limits

- **A judge who rejects without a delta:** `pop_move` refuses the route.
- **A judge who proposes or applies a correction:** a violation of independence; the correction belongs to the executor relaunched by the orchestrator.
- **3rd failure of the same route:** `circuit_breaker: true`.
- **The `phase-verification` task:** an execution defect of an already-closed task of the phase is a fix inside it; a structural defect (a wrong durable contract, an unmet request) becomes a modification/new task — a deleted folder is never reopened.
- **Limit:** the judge is a yolo-only figure; outside it the gate is the human PR.

## Conformance criteria

- [x] Exactly one judge per round, at any `size`/`critical`.
- [x] The `.verify.md` cap is machine-validated; the pair's artifacts are a violation in a card created on or after the cutoff.
- [x] No new frontmatter field; the three exits and the two counters remain.
- [x] A test criterion is born `verify: phase` and runs only in the phase's verification task.
- [x] Every roadmap phase ends with the `phase-verification` task.

## Out of scope

- The judgment's internal procedure: the [[.agents/skills/judge-dredd/SKILL|judge-dredd]] skill.
- The operational norm of phase verification: [[WORKFLOW|WORKFLOW]] › "Phase verification".
- Return routes and the state machine: [[specs/multi-agent-orchestration|multi-agent orchestration]] and [[WORKFLOW|WORKFLOW]].

## Related references

- [[specs/adversarial-gate|Adversarial gate]] — *superseded: consult only to understand the history of the advocate + judge pair (2026-07-27 → 2026-08-04)*.
- [[specs/multi-agent-orchestration|Multi-agent orchestration]] — *always follow: the live role contract; the `005_closing` gate uses exactly one judge per round*.
- [[_templates/TASK-VERIFY|TASK-VERIFY]] — *follow when writing the `.verify.md`*.
