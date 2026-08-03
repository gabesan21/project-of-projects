# Verification and critique — [[<id>-<slug>]]

> Blockquotes are filling instructions — **delete them when filling**.

- **Stage:** 005_closing (act 1) · **Owner:** independent reviewer

> **Artefact exclusive to `yolo: true`.** Outside yolo there is no agentic reviewer: the gate is the human PR and this file is never created.
> One fresh-context agent verifies behavior and quality, **medium** tier (WORKFLOW matrix), and selects `differential|full`: `full` for critical tasks or a `premissa` return; after a `lacuna` or an execution failure, the differential covers the **delta**. Inconclusive evidence is re-run.
> **An environment failure never returns.** A criterion blocked by sandbox/infra or flaky evidence gets a `qualified pass (environment)` with the alternative evidence available and joins the verdict's human checklist; a return demands a reproducible product defect. A `verify: user` criterion is not judged here — it goes straight to the checklist.
> This is the single quality gate (003 exists only for `critical: true`). Answer **first** whether the original request — the card's What/Why — was met; only then validate specs and the plan's criteria.
> **Three exits, not two:** approved; **execution blocker** → 004, when the executor did not meet the criteria it received; **plan defect** → 002, when the criteria did not cover the card's request and the executor delivered what it was given. Plan adherence that misses the request is never the executor's failure.
> **You name the delta, you do not fix the defect.** Dispatching the correction would turn you into whoever commissioned the work you judge.

## Round 1 — YYYY-MM-DD

- **Strategy:** differential | full — <reason>.
- **Surface:** <covered diff/risks>.
- **Returns:** execution 0 | 1 | 2 of 2 · plan 0 | 1 | 2 of 2 — failure 3 on the same route activates the circuit breaker.

### Objective and spec conformance

| # | Criterion | Mode | Verification run | Result | Evidence |
|---|---|---|---|---|---|
| 1 | <plan criterion> | re-run \| evidence | `<run>` or <audited artifact> | passed \| failed \| qualified pass (environment) | <observed versus expected> |

### Implementation quality

| Severity | Finding | Evidence | Required correction |
|---|---|---|---|
| blocking \| suggestion \| nit | <problem> | `<file:line>` or run | <objective action> |

### Scope and integration

- [ ] Changes respect every front's `Owns` and `Must not edit`.
- [ ] Consumers did not opportunistically implement dependencies.
- [ ] Aggregate gate passed after integration.
- [ ] Affected specs, docs and DOX contracts are coherent.

## Verdict

- **Decision:** approved → delivery and close-out | **directed repair** (pinpoint delta — not a route and no counter; the orchestrator dispatches the patch and you check it in a ≤10-line addendum this round; max 2 per round) | execution blocker → 004_processing | plan defect → 002_planning | circuit breaker.
- **Blocking findings:** none | <short list>.
- **Plan defect:** none | <criterion that did not cover the card's request>.
- **Suggestions/nits:** <non-blocking; record only when useful>.
- **Human checklist:** none | <`verify: user` criteria and qualified passes (environment), with the manual step and the expected pass — the orchestrator carries them into the PR/final approval>.
- **Summary:** <brief comparison of initial objective and implemented result>.

## Delta of the return

> **Mandatory on every verdict that is not an approval** — delete the section only when approving. Without a delta, 002 cannot tell whether to amend or replan and 004 re-executes already approved work. The orchestrator carries the type with `pop_move --return-kind <type>`.
> **`lacuna`** = the criteria did not cover the request, but what was delivered is correct → 002 **appends** a criterion/front, without renumbering or rewriting. **`premissa`** = the strategy was wrong and what was delivered is on the wrong path → real replanning. **`execucao`** = the executor did not deliver what it received → 004.

- **Type:** lacuna | premissa | execucao.
- **Affected criteria:** <plan IDs> — <what is missing or failed, one line>.
- **Affected fronts:** `<Fxx>` — they re-enter 004 (or: a new front to create in 002).
- **Untouched fronts:** `<Fxx>` — approved, they stay integrated; do **not** re-execute.
- **Expected action:** <one line: what 002 amends or what 004 fixes>.

> On approval, write the memory in the same session — you have just read the diff: the ledger `memory/<YYYY-MM-DD>/<id>.md` plus one entry `<id>.<nn>-<slug>.md` per thing done, with linked evidence ([[_templates/MEMORY|MEMORY]] · [[_templates/MEMORY-ENTRY|MEMORY-ENTRY]]). Integration, PR and merge remain the orchestrator's and the human's job.
