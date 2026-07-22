# Verification and critique — [[<id>-<slug>]]

> Blockquotes are filling instructions — **delete them when filling**.

- **Stage:** 005_verifying · **Owner:** independent reviewer

> One fresh-context agent verifies behavior and quality. In yolo it is always **strong** and selects `differential|full`; full is mandatory for critical tasks or after a return.
> **Yolo:** this is the single quality gate (003 exists only for `critical: true`). Answer **first** whether the original request — the card's What/Why — was met: without plan approval the brief is strategy, not contract; a plan deviation that serves the request is not a failure, plan adherence that misses the request is blocking.

## Round 1 — YYYY-MM-DD

- **Strategy:** differential | full — <reason>.
- **Surface:** <covered diff/risks>.
- **Yolo return:** 0 | 1 | 2 of 2 — failure 3 activates the circuit breaker.

### Objective and spec conformance

| # | Criterion | Mode | Verification run | Result | Evidence |
|---|---|---|---|---|---|
| 1 | <plan criterion> | re-run \| evidence | `<run>` or <audited artifact> | passed \| failed | <observed versus expected> |

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

- **Decision:** approved → 006_done | rejected → 004_processing | circuit breaker.
- **Blocking findings:** none | <short list>.
- **Suggestions/nits:** <non-blocking; record only when useful>.
- **Summary:** <brief comparison of initial objective and implemented result>.

## Human approval (only `critical: true` outside yolo)

### Human response

_(write here)_

- [ ] Done
