# Accusation — [[<id>-<slug>]]

> Blockquotes are filling instructions — **delete them when filling**.

- **Stage:** 005_closing (act 1) · **Owner:** devil's advocate

> **Adversarial-gate artifact.** It is born only when the task is `yolo: true` **and** (`size: L` **or** `critical: true`); in that configuration there is no `.verify.md`. Fresh context, **strong** tier, distinct from planner, executor and judge.
> **One file per round:** save it as `<id>.r<n>.accusation.md`, starting at `r1`. A new round never overwrites the previous one; rounds are never deleted, and the highest `n` is the one that decides.
> **Ceiling: 50 lines per round** (validated by `pop_validate`). Record only actionable findings, with a source.
> **You accuse; the judge decides.** Do not choose a route, do not approve, do not reject and do not write the task memory — an accusation is not a verdict. Nor do you fix what you pointed at.
> Walk both **axes** and keep them apart: **execution** (the plan's criteria re-run and the quality of the diff) and **decision** (attacking the choices declared in the [[<id>-<slug>.defense|defense]]).
> Every item carries severity, evidence and a remedy. An item without all three is an invalid artifact and is reissued before the judge rules.

## Execution axis — criteria re-run

| # | Plan criterion | Verification performed | Result | Evidence |
|---|----------------|------------------------|--------|----------|
| 1 | <criterion> | `<run>` or <artifact audited> | passed \| failed | <observed versus expected> |

### Execution objections

| Severity | Objection | Evidence | Remedy |
|----------|-----------|----------|--------|
| blocking \| suggestion \| nit | <what is wrong in the diff or in the result> | `<file:line>` or run | <the objective action that would resolve it> |

## Decision axis — attacking the defense

| Severity | Decision attacked | Objection | Evidence | Remedy |
|----------|-------------------|-----------|----------|--------|
| blocking \| suggestion \| nit | <the decision's number in the defense> | <why the choice does not hold> | <observed falsifier, `file:line` or run> | <the objective action that would resolve it> |

## Result

> **"No material objection" is a valid and successful verdict of this role** — an advocate that must always accuse is noise, not a gate. Declare it here, with the same seriousness as an accusation, when the axis passes; the judge rules on that record as it would on any other.

- **Execution axis:** no material objection | <n> objections (<n> blocking).
- **Decision axis:** no material objection | <n> objections (<n> blocking).
- **Surface covered:** <the diff, criteria and risks actually examined>.
- **Not examined:** nothing | <what was left out and why>.
