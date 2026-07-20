# Verification and critique — [[<id>-<slug>]]

> Blockquotes are filling instructions — **delete them when filling**.

- **Stage:** 005_verifying · **Owner:** independent reviewer

> One fresh-context agent verifies behavior and quality. Read objective, specs, DOX contracts and diff; do not depend on the execution narrative. `critical: true` raises depth/model, not reviewer count.

## Round 1 — YYYY-MM-DD

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

- **Decision:** approved → 006_done | rejected → 004_processing.
- **Blocking findings:** none | <short list>.
- **Suggestions/nits:** <non-blocking; record only when useful>.
- **Summary:** <brief comparison of initial objective and implemented result>.

## Human approval (only `critical: true` outside yolo)

### Human response

_(write here)_

- [ ] Done
