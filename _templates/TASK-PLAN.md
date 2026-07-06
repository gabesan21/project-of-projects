# Plan (wargame) — [[<id>-<slug>]]

> Blockquotes in this template are fill-in instructions — **delete them when filling it in**.

- **Stage:** 002_planning · **Owner:** agent

> You are not executing the task — you are **wargaming** the execution. Whoever runs the plan in 004 may be a simpler executor: write so they can execute **without asking a single question**. Limit: **200 lines** (documented exception to the ~150 rule); detailed moves live in the groups under `subtasks/`. Went over 200 → the task is too big: propose splitting it into more tasks chained by `depends_on`.

## Recon

> Prior reading, read-only, **before** planning: specs, affected code/material, references. On research-heavy boards, fire off **parallel subagents** — one per investigation front — and consolidate here.

- <source read> — what it established, in one line.

### RECON NEEDED

> Assumptions recon did not resolve. Each one with the **exact check** that resolves it and in which move it runs.

- [ ] <assumption> — check: <command/reading that confirms or kills it> (in group <gNN>).

## Route

How the task will be executed, in a few paragraphs. Discarded alternatives in one line each, if relevant.

## Forks

> **Pre-authorized** alternative routes, each with an objective trigger. No trigger means it is not a fork — it is a return to the human (002).

- If <X> is observed (in move <ref>) → <route B, in one line>.

## Abort conditions

> The moments to **stop and signal** (`blocked: true` + reason) instead of improvising.

- <objective condition that ends the execution>.

## Acceptance criteria and verification

> This is the table 005 runs against — each criterion with the exact run and what a pass looks like. The `.verify.md` is born from it.

| # | Criterion | Verification run | Pass looks like |
|---|-----------|------------------|-----------------|
| 1 | <objective and checkable> | `<command>` or reading of <where> | <what should be observed> |

## Change specs

> Drafted **here** (draft via `write-spec`), approved together with the 003 gate, synced with the project specs in 006 (`sync-specs`).

- [[<category>/<project>/specs/<spec>|<spec>]] — what changes in it, in one line.

## Minimal executor context

> A **closed** list, assembled in the wargame: everything the 004 executor reads. Outside it, only with a fork trigger.

- <file/spec/contract> — what it answers, in one line.

## Groups

One file per group in `subtasks/` ([[_templates/SUBTASKS|template]]), with the detailed moves (expected observation, likely failure → counter-move):

1. [[<id>-<slug>.g01-<group-slug>]] — one line about the group.
2. [[<id>-<slug>.g02-<group-slug>]] — ...

## Red-team

> **Mandatory** before 003 — waive only on a trivial task of very few steps, recording the waiver in one line. Attack your own plan (or ask a subagent with a clean context) and record:

- **Attack that failed against the plan:** <the attack and why the plan held>.
- **Attack that got through → patch:** <what broke through> → <what changed in the plan because of it>.
