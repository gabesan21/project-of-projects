# Plan (wargame) — [[<id>-<slug>]]

> Blockquotes in this template are fill-in instructions — **delete them when filling it in**.

- **Stage:** 002_planning · **Owner:** agent

> You are not executing the task — you are **wargaming** the execution. Whoever runs the plan in 004 may be a simpler executor: write so they can execute **without asking a single question**. Ceremony proportional to the card's `size`: **S = a mini-plan of ≤40 lines** (route, preflight, criteria — no delegated recon, red-team and forks not required). General limit: **200 lines** (documented exception to the ~150 rule); detailed moves live in the groups under `subtasks/`. Went over 200 → the task is too big: propose splitting it into more tasks chained by `depends_on`.

## Recon

> Prior reading, read-only, **budgeted**: start from the researches and specs linked on the card; then list the questions the plan needs and you cannot answer — only a question above rule 18's floor (~5K tokens of reading) becomes a worker, in waves of **3-5**; **0 workers is valid**. Each report carries a **source (file/line) per finding** and a **"Gaps / Not found"** section (it feeds RECON NEEDED); workers spawn no subagents. **No web** — a knowledge gap becomes a prompt in `RESEARCHES.md` + `blocked` (see WORKFLOW 002); a one-off lookup via command is allowed and recorded here.

- <source read> — what it established, in one line.

### RECON NEEDED

> Assumptions recon did not resolve. Each one with the **exact check** that resolves it and in which move it runs.

- [ ] <assumption> — check: <command/reading that confirms or kills it> (in group <gNN>).

### Environment preflight

> A cheap battery, run **directly** by the planner: runtime and tool versions the plan depends on. An unverified environment assumption is the classic cause of a 004→002 return.

- `<command>` → <what was observed> (e.g. `node --version` → v24.x).

## Route

How the task will be executed, in a few paragraphs. Discarded alternatives in one line each, if relevant.

## Forks

> **Pre-authorized** alternative routes, each with an objective trigger. No trigger means it is not a fork — it is a return to the human (002).

- If <X> is observed (in move <ref>) → <route B, in one line>.

## Abort conditions

> The moments to **stop and signal** (`blocked: true` + reason) instead of improvising.

- <objective condition that ends the execution>.

## Acceptance criteria and verification

> This is the table 005 runs against — each criterion with the exact run, what a pass looks like and the **005 mode**: `re-run` (observable external behavior — the verifier re-executes) or `evidence` (the verifier audits the output captured by the executor). A task with a runtime surface requires **≥1 `re-run`**. Prefer the project's **aggregated gate** over N separate runs — an individual run only for what it doesn't cover. The `.verify.md` is born from it. **Yolo task:** a criterion without an executable run and an observable "Pass looks like" will be **sent back by the critic** in 003 — nothing subjective.

| # | Criterion | Verification run | Pass looks like | 005 |
|---|-----------|------------------|-----------------|-----|
| 1 | <objective and checkable> | `<command>` or reading of <where> | <what should be observed> | re-run \| evidence |

## Change specs

> Drafted **here** (draft via `write-spec`), approved together with the 003 gate, synced with the project specs in 006 (`sync-specs`).

- [[categories/<category>/<project>/pop/specs/<spec>|<spec>]] — what changes in it, in one line.

## Minimal executor context

> A **closed** list, assembled in the wargame: everything the 004 executor reads. Outside it, only with a fork trigger.

- <file/spec/contract> — what it answers, in one line.

## Groups

One file per group in `subtasks/` ([[_templates/SUBTASKS|template]]), with the detailed moves (expected observation, likely failure → counter-move):

> **Yolo task:** avoid `(user)` items — the critic does not perform real-world human actions; an unavoidable `(user)` item blocks the task (`blocked: true`) and hands it back to the human via the INBOX.

1. [[<id>-<slug>.g01-<group-slug>]] — one line about the group.
2. [[<id>-<slug>.g02-<group-slug>]] — ...

## Red-team

> **Mandatory for size M/L**, before 003 — waived in S, recording the waiver in one line. Attack your own plan (or ask a subagent with a clean context) and record:

- **Attack that failed against the plan:** <the attack and why the plan held>.
- **Attack that got through → patch:** <what broke through> → <what changed in the plan because of it>.
