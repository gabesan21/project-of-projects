# Plan — [[<id>-<slug>]]

> Blockquotes are filling instructions — **delete them when filling**.

- **Stage:** 002_planning · **Owner:** planner agent

> The planner is separate from the executor. This file stores the planning result: a brief sufficient for capable agents, without reasoning, pseudocode, implementation snippets or step-by-step edits. Target: ≤80 lines; ceiling ~150. If fronts do not fit, propose chained tasks through `depends_on`.

## Objective and expected result

- **Objective:** <what must change>.
- **Observable result:** <how the user or system perceives delivery>.

## Strategy

A few paragraphs covering the base approach, execution-constraining decisions and broad order. Durable detail belongs in specs; operational detail belongs to executors.

## Affected areas

- `<subtree, module or artifact>` — why it may change.

## Gaps and preflight (only if applicable)

- **RECON NEEDED:** <assumption> — check: <exact reading/command>.
- **Preflight:** `<command>` → <required environment observed>.

## Execution fronts

> A front is an ownership unit, not an edit list. Use [[_templates/SUBTASKS|SUBTASKS]] only when a front needs its own file. Fronts without logical dependencies **and** without write overlap may run in parallel; others run in waves.

### <F01> — <name>

- **Delivery:** <result of this front>.
- **Scope:** <functional boundary>.
- **Owns:** `<files or patterns it may edit>`.
- **May read:** `<allowed/recommended context>`.
- **Must not edit:** `<write boundaries>`.
- **Depends on:** `<Fxx>` | none.
- **Expected input:** <contract or artifact produced by dependency> | none.
- **Skills:** [[categories/<category>/<project>/pop/skills/<skill>|<skill>]] — *use for <trigger>*.
- **Criteria:** <IDs of criteria below satisfied by this front>.

> Missing/incompatible dependency or expected input → report `BLOCKED` to the orchestrator. Never implement, simulate or repair the dependency autonomously.

## Order and parallelism

> Represent the DAG in waves. Parallelism requires logical and write independence.

1. **Wave 1:** F01.
2. **Wave 2:** F02 and F03 in parallel after F01.
3. **Integration:** orchestrator validates ownership, integrates results and runs the aggregate gate.

## Risks and abort conditions

- **Risk:** <impact> — mitigation: <control>.
- **Abort if:** <objective condition> — set `blocked: true` with <evidence>.

## Acceptance criteria

| # | Criterion | Verification | Pass looks like | 005 mode |
|---|---|---|---|---|
| 1 | <behavior or contract> | `<command>` or read <artifact> | <objective observation> | re-run \| evidence |

## Specs and contracts

> Link durable contracts; do not copy them. Create/change a spec only when delivery changes durable behavior, interface or invariant.

- [[categories/<category>/<project>/pop/specs/<spec>|<spec>]] — *follow for <contract>; expected change: <one line or none>*.
- [`<subtree>/AGENTS.md`](../<path-in-repo>/AGENTS.md) — *follow before changing <area>*.

## Execution topology

- **Shape:** single executor | sequential specialists | parallel specialists | hybrid waves.
- **Rationale:** <skills, dependencies and write boundaries that determine the shape>.
- **Model/tier by role:** <only when the choice matters>.
