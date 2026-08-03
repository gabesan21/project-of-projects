# Judgment — [[<id>-<slug>]]

> Blockquotes are filling instructions — **delete them when filling**.

- **Stage:** 005_closing (act 1) · **Owner:** judge

> **Adversarial-gate artifact.** It is born only when the task is `yolo: true` **and** (`size: L` **or** `critical: true`), after the [[<id>-<slug>.r<n>.accusation|accusation of the same round]] and in a context fresh and separate from it; in that configuration there is no `.verify.md`.
> **One file per round:** save it as `<id>.r<n>.judgment.md`, with the same `n` as the accusation it rules on, starting at `r1`. A new round never overwrites the previous one; rounds are never deleted, and the highest `n` is the one that decides.
> **Ceiling: 40 lines per round** (validated by `pop_validate`). Rule on what was accused; do not redo the whole review.
> **You name the delta, you do not fix the defect** — neither apply the correction nor dispatch it to anyone: a gate that commissions its own fix stops being a gate. The correction belongs to the executor relaunched by the orchestrator.
> Answer **first** whether the original request — the card's What/Why — was met; only then rule on the accusations. Plan adherence that does not meet the request is never the executor's failure.
> **An environment failure never sustains a blocker.** An objection whose damage depends on infrastructure beyond the agent's reach (sandbox, flakiness) is dismissed as blocking: the item becomes a qualified pass and joins the verdict's human checklist.

## Original request

- **Met:** yes | no — <one line comparing what the card asked for with what was delivered>.

## Item-by-item judgment

| # | Objection (axis) | Judgment | Reason |
|---|------------------|----------|--------|
| 1 | <objection from the accusation> (execution \| decision) | upheld \| dismissed | <one line> |

> An accusation that declared **"no material objection"** is a well-formed accusation: rule on that record like any other — agreeing, or pointing out with evidence what it let through.
> **An invalid accusation is not ruled on and produces no file.** An item without severity, evidence or remedy — or an accusation above 50 lines — interrupts the judgment: **do not write this file**; report to the orchestrator, which relaunches the advocate in the same round. It is not a route, it consumes no return counter, and it is recorded in the card Log. A second invalid accusation in a row → `blocked: true`.

## Verdict

- **Decision:** approved → act 2 | **directed repair** (pinpoint delta — not a route and no counter; the orchestrator dispatches the patch and you check it in a ≤10-line addendum this round; max 2 per round) | execution blocker → 004_processing | plan defect → 002_planning | circuit breaker.
- **Blocking objections upheld:** none | <short list>.
- **Suggestions/nits accepted:** <they do not block; record only if useful>.
- **Human checklist:** none | <`verify: user` criteria and qualified passes (environment), with the manual step and the expected pass>.
- **Returns:** execution 0 | 1 | 2 of 2 · plan 0 | 1 | 2 of 2 — the 3rd of the same route opens the circuit breaker.

## Return delta

> **Mandatory in every verdict that is not an approval** — delete the section only when approving. Fill it **in the form** of the "Return delta" section of [[_templates/TASK-VERIFY|TASK-VERIFY]], which is the source of the types and the fields: follow that template instead of reproducing it here, so that a change there automatically applies here. The orchestrator carries the type with `pop_move --return-kind <type>`.

_(fill in as per [[_templates/TASK-VERIFY|TASK-VERIFY]] › "Return delta")_

> On approval, write the memory in the same session — you have just read the diff and the accusation: the ledger `memory/<YYYY-MM-DD>/<id>.md` plus one entry `<id>.<nn>-<slug>.md` per thing done, with linked evidence ([[_templates/MEMORY|MEMORY]] · [[_templates/MEMORY-ENTRY|MEMORY-ENTRY]]). Integration, PR and merge remain the orchestrator's and the human's job.
