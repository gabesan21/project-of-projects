# Front <F01> — <name> — [[<id>-<slug>]]

> Optional: create only when a front has distinct ownership, owner or dependency worth tracking. Do not describe code or micro-edits.

- **Delivery:** <result>.
- **Scope:** <functional boundary>.
- **Owner:** agent | user.
- **Owns:** `<files or patterns it may edit>`.
- **May read:** `<specs, contracts and areas available for consultation>`.
- **Must not edit:** `<reserved files, areas and fronts>`.
- **Depends on:** `<Fxx>` | none.
- **Expected input:** <dependency contract/artifact> | none.
- **Skills:** [[categories/<category>/<project>/pop/skills/<skill>|<skill>]] — *use for <trigger>*.
- **Criteria:** <IDs from the [[<id>-<slug>.plan|plan]]>.

## Execution contract

- Deliver only this front's scope and criteria.
- Missing/incompatible dependency or input → respond `BLOCKED` with evidence.
- Do not implement, simulate or repair dependencies autonomously.
- Do not edit paths outside `Owns`; return new needs to the orchestrator.

## Result

- **Status:** completed | BLOCKED.
- **Commit/artifact:** <reference>.
- **Changed files:** <short list checked against `Owns`>.
- **Divergences:** none | <divergence and orchestrator authorization>.
- **Evidence:** <relevant gate or observation>.
