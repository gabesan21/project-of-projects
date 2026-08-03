---
id: adversarial-gate
project: pop
domain: harness
kind: contract
status: active
implementation: implemented
origin: "8.1"
created: 2026-07-27
updated: 2026-08-03
supersedes: []
superseded_by:
---

# Spec — Adversarial gate

## Contract

In a `yolo: true` task of higher consequence, act 1 of `005_closing` stops being judged by a single reviewer and is judged by a **pair**: a **devil's advocate**, who accuses, and a **judge**, who decides. The pair **replaces** the independent reviewer in that configuration — it is never added to it — and the pair exists only where the trigger fires.

Act 1 remains **one stage with an internal fork**, never two flows: the same input (card, plan, specs, diff), the same three exits and the same counters; only the number of judging contexts and what each may do change.

## Expected behavior

- Given a task with `yolo: true` **and** (`size: L` **or** `critical: true`), when it enters act 1 of `005_closing`, then the devil's advocate and, after them, the judge run in fresh separate contexts — and there is **no** independent reviewer in that round.
- Given a task with `yolo: true` and `size: S`/`M` **without** `critical: true`, when it enters act 1, then the standing configuration applies: exactly **one** strong independent reviewer per round, and no artifact of the pair is born.
- Given a task with `yolo: false`, when it reaches `005_closing`, then there is neither an agentic reviewer nor an adversarial gate: the gate is the human PR, and with no PR (root local scope) there is no verification gate.
- Given the 002_planning of a task that satisfies the trigger, when the plan is written, then the planner also delivers the **defense** (`.defense.md`) — without it the advocate has nothing to attack.
- Given the advocate, when it concludes with no material finding, then it records **"no material objection"** as a valid and successful verdict, and the judge rules on that record as on any other.
- Given the judge, when it decides, then it issues exactly one of the three existing exits and, when it is not an approval, names the delta in the form of the "Return delta" section of [[_templates/TASK-VERIFY|TASK-VERIFY]].
- Given a decision contested and upheld in the judgment, when it passes the three harvest tests of act 3 of [[WORKFLOW|WORKFLOW]] › `005_closing`, then the gate produces a durable record in the right place — a line in a spec for a contract, invariant or interface; a note in `notes/decisions/` for the reason behind a choice; otherwise it dies in the task memory's entries, and the absence of a harvest is not recorded.

### Act-1 sequence — configuration A (adversarial pair)

1. The orchestrator checks the trigger in the card frontmatter (`yolo`, `size`, `critical`) and selects the configuration.
2. **Devil's advocate**, fresh context, strong tier: receives the card, the plan, the defense, the specs and the diff. Walks two axes — **execution** (re-running the plan's criteria, quality review with `clean-code-review` in code) and **decision** (attacking the choices declared in the defense). Produces the `.accusation.md`.
3. **Judge**, fresh and separate context, strong tier: receives card, plan, defense, accusation and diff. Rules on each accusation as upheld or dismissed, first checks whether the card's **original request** was met, and issues verdict and route. Produces the `.judgment.md`.
4. Approved → act 2. Rejected → the orchestrator carries the delta with `pop_move --return-kind <type>` and relaunches the indicated route.

### Act-1 sequence — configuration B (single reviewer)

1. The orchestrator checks the trigger and selects the configuration.
2. **Independent reviewer**, fresh context, medium tier (WORKFLOW matrix): checks original request, criteria, specs, diff and quality; produces the `.verify.md`.
3. Approved → act 2. Rejected → delta and route, as before.

### Exits and owner of the next action

| Exit | Route | Counter | Owner of the next action |
|------|-------|---------|--------------------------|
| Approved | act 2 (integration/delivery) | — | orchestrator (integrates/PR); the judge writes the memory ledger and entries in the same session in which it approves |
| Execution blocker | → `004_processing` | `yolo_005_returns` | orchestrator relaunches the executor of the delta's fronts |
| Plan defect | → `002_planning` | `yolo_003_returns` | orchestrator relaunches the planner (amendment for `lacuna`, replanning for `premissa`) |

## Invariants

- **The advocate's powers:** accuse, re-run the plan's criteria and review the diff's quality. **The advocate's prohibitions:** choosing a route, approving, rejecting or writing memory — an accusation is not a verdict.
- **The judge's powers:** rule on each accusation, decide the exit, name the delta and write the memory on approval. **The judge's prohibitions:** fixing what it rejected or dispatching the correction — a gate that commissions its own fix stops being a gate.
- Advocate and judge are contexts distinct from each other and from planner and executor; none of them executes the solution it judges.
- Where the pair runs, the independent reviewer does **not**; where the reviewer runs, neither advocate nor judge does. Never all three.
- The trigger is entirely derivable from the card frontmatter: `yolo: true` **and** (`size: L` **or** `critical: true`). No new mark in the roadmap, the card or the plan fires the gate.
- The counters are exactly the two existing ones — `yolo_005_returns` (execution) and `yolo_003_returns` (plan) — with two returns per route and `circuit_breaker` on the 3rd failure of the same route. A new counter would be a new loop.
- The defense is a short list of contestable decisions, **never** chain-of-thought, pseudocode or a transcript of reasoning.
- "No material objection" is a valid and successful result of the advocate; an advocate that must always accuse is noise, not a gate.
- Every return, in any configuration, carries a classified delta (`lacuna` | `premissa` | `execucao`); the re-entry covers only the delta, the re-review is differential over it and **expensive evidence is reused** — a capture matrix, a long battery or a costly run only regenerates the slice affected by the delta.
- **Directed repair:** an execution blocker with a pinpoint delta (named `file:line`, objective remedy, no strategy change) is not a route — the orchestrator dispatches a medium executor with only the delta and whoever judged checks the repair in the same round, in a ≤10-line addendum within the cap; it consumes no counter. At most two directed repairs per round; the third becomes a route.
- **An environment failure never returns:** a criterion blocked by sandbox/infra or flaky evidence gets a qualified pass with alternative evidence and joins the delivery's human verification checklist; a return demands a reproducible product defect. A `verify: user` criterion is not judged by the gate.
- **The gate does not expand the scope:** a finding outside the card's What/Why becomes a traceable follow-up, never a new criterion or front of the task; a `lacuna` fits once per task — the second closes the task and the rest is born as its own task.
- **Progress breaker:** a return whose delta repeats the previous one's theme with no new fact opens the circuit breaker early, before the 3rd failure.

## Interfaces

Three kanban artifacts, each specified by **who writes it · where it is born · what it carries · cap**.

| Artifact | Who writes | Born in | What it carries | Cap |
|----------|------------|---------|-----------------|-----|
| `<id>.defense.md` | planner | `002_planning` | the plan's contestable decisions; per decision: the choice adopted, the alternative rejected, why, and what would falsify it | ≤30 lines |
| `<id>.r<n>.accusation.md` | devil's advocate | `005_closing` (act 1) | one item per objection, with **severity** (blocking \| suggestion \| nit), evidence (file:line or run) and **the remedy** that would resolve it; execution axis (criteria re-run) and decision axis; "no material objection" when that is the case | ≤50 lines per round |
| `<id>.r<n>.judgment.md` | judge | `005_closing` (act 1) | item-by-item judgment (upheld \| dismissed, with a reason), verdict, the route chosen and, when it is not an approval, the delta in the form of the "Return delta" section of [[_templates/TASK-VERIFY\|TASK-VERIFY]] | ≤40 lines per round |

- **One pair of files per round:** the pair's artifacts carry the round infixed before the suffix — `<id>.r<n>.accusation.md` and `<id>.r<n>.judgment.md` — starting at `r1`. A new round **never** overwrites or deletes the previous one; the highest `n` is the one that decides, and the earlier ones remain as proof. The 50- and 40-line caps apply **per round**, not to the sum of the history.
- **Gate input:** the card (`What`/`Why` and frontmatter), the plan and its criteria, the defense, the linked specs and the integrated diff.
- **Gate output:** the `.judgment.md` in configuration A or the `.verify.md` in configuration B; in both cases, one of the three routes and, when there is a return, `return_kind` written by `pop_move`.
- **Compatibility:** the `.judgment.md` **references** the "Return delta" section of the TASK-VERIFY, it does not copy it; a change in that section applies to the judge automatically.

## Errors and limits

- **A missing defense in a task that satisfies the trigger:** a mechanical amendment — the orchestrator dispatches a planner to produce it on the spot, with no route, no counter and no folder move, and act 1 runs next; a 005→002 cycle over a missing process artifact is not a gate. Pre-cut-off cards follow the transition clause of act 1 of [[WORKFLOW|WORKFLOW]] (they run in configuration B).
- **An accusation above the cap, or an item without severity/evidence/remedy:** an invalid artifact; the judge neither rules nor writes the `.judgment.md`, and the **orchestrator** relaunches the advocate to reissue in the same round, recording it in the card Log. It is not a route and consumes no counter; a second invalid accusation in a row becomes `blocked: true`.
- **A judge that rejects without a delta:** `pop_move` refuses the route — with no type there is no way to decide between amendment and replanning.
- **A judge that proposes or applies a correction:** a violation of independence; the correction belongs to the executor relaunched by the orchestrator.
- **The 3rd failure of the same route:** `circuit_breaker: true`, in either configuration.
- **Limit:** the pair is a yolo-only figure; no configuration of this contract creates an agentic reviewer outside it.

## Conformance

- [x] The trigger is evaluated only from the card's `yolo`, `size` and `critical`, and the three situations (pair, single reviewer, no reviewer) are mutually exclusive.
- [x] In configuration A there is no `.verify.md`; in configuration B there is neither `.accusation.md` nor `.judgment.md`.
- [x] Advocate and judge run in separate contexts, in this order, both strong.
- [x] The caps of the three artifacts are machine-validated.
- [x] No new frontmatter field is introduced for the gate.
- [x] The three exits and the two counters behave identically in both configurations.
- [x] "No material objection" is accepted by the judge as a well-formed accusation.

## Related references

- [[specs/multi-agent-orchestration|Multi-agent orchestration]] — *always follow: it is the standing role contract; the invariant "the `005_closing` gate uses exactly one independent reviewer per round" now has **two configurations***.
- [[_templates/TASK-VERIFY|TASK-VERIFY]] — *follow when writing the `.judgment.md`: the verdict and the "Return delta" section are reused by reference*.
- [[WORKFLOW|WORKFLOW]] — *follow for act 1 of `005_closing` and the standing return routes*.
