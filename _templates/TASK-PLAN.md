# Plan — [[<id>-<slug>]]

> Blockquotes are filling instructions — **delete them when filling**.

- **Stage:** 002_planning · **Owner:** planner agent

> The planner is separate from the executor. This file stores the planning result: a brief sufficient for capable agents, without reasoning, pseudocode, implementation snippets or step-by-step edits.
> **Ceiling: 80 lines, at any `size`** (validated by `pop_validate`). This is the slice everyone reads, so it does not grow with the task — what grows is the number of front files. Not fitting means **modularizing** into `subtasks/`, never compressing to the point of losing a decision. Splitting the task through `depends_on` is the exception, for when the fronts do not share an objective.

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

> A front is an ownership unit, not an edit list. **Every front that goes to a separate context gets its own file** in `subtasks/` ([[_templates/SUBTASKS|SUBTASKS]], ≤50 lines) — it is that executor's reading slice; here stays only the summary line and the link. A single-front task has no `subtasks/`: the executor reads the plan, which is already short. Fronts without logical dependencies **and** without write overlap may run in parallel; others run in waves.

### <F01> — <name>

- **Delivery:** <result of this front>.
- **Contract:** [[<id>-<slug>.g01-<front-slug>]] — *follow it as this front's single execution slice* (omit when the task has a single front: the fields below suffice).
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

> Observable criteria, compared at the `005_closing` gate. They are **the contract**: they bind the executor and the gate, and they must cover the card's What/Why — a criterion that does not cover the request is a plan defect and comes back here. Prefer the aggregate gate. A runtime surface requires at least one `re-run`.
> **Append-only between rounds:** a `lacuna` return adds a row and keeps existing IDs — renumbering a criterion or a front breaks the references in `.verify.md` and in telemetry, and forces the re-review to start from scratch.

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
