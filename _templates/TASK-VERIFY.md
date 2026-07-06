# Verification — [[<id>-<slug>]]

- **Stage:** 005_verifying · **Owner:** agent (+ user if `critical: true`)

> Copy the "Acceptance criteria and verification" table from the [[<id>-<slug>.plan|plan]] and execute **each run in the task's worktree**, comparing what was observed with the "Pass looks like" defined there. A criterion failed → the task goes back to `004_processing` — see [[WORKFLOW|WORKFLOW]].

## Round 1 — YYYY-MM-DD

| # | Criterion | Run executed | Result | Evidence |
|---|-----------|--------------|--------|-----------|
| 1 | <criterion from the plan> | `<run from the plan>` | ✅ passed / ❌ failed | What was observed vs. the "Pass looks like", in one line. |

**Verdict:** approved → 006_done | rejected → 004_processing (<what is missing>)

## Human approval (only if `critical: true`)

### Human response

_(write here)_

- [ ] Done
