---
author: user
date: 2026-07-22
---

# Harness decisions — 2026-07-22

## Yolo has a single quality gate in 005

A non-critical `yolo: true` task transits 002 → 004 directly, without an approval round — yolo trusts the agent's plan. The 005 (strong critic, clean session) is the decisive gate and checks **first whether the original request** (the card's What/Why) was met: without a 003 approval, the brief is strategy, not contract — a plan deviation that serves the request is not a failure; plan adherence that misses the request is blocking. `critical: true` is the exception: it keeps 003 with a strong critic. Circuit breakers unchanged (two returns per gate; the third goes to the human).

**Rationale:** yolo's cost was in the double strong review (003 + 005); the human gates were already delegated. Judgment is concentrated where the evidence exists (post-execution), keeping protection for what is critical.

## Human merge respects the marked yolo scope

The human merge (the `develop` → `main` PR in external projects) happens at the end of the scope the human marked as yolo: single task, phase/epoch or modification — never earlier.

**Rationale:** it honors the delegation as the human defined it; batch review at the level they chose.

## Modifications replace Epoch 0

Epoch 0 ("continuous", created on demand) is retired. Whatever arrives **outside the plan** — hotfixes, tweaks, contract fixes/changes and small emergent features — lives in `MODIFICATIONS.md` + `modifications/`, next to the ROADMAP, in two levels: modification `M-<n>` (one line in the index; detail in `modifications/m-<n>-<slug>.md` only when multi-task) → task `M-<n>.<t>-<slug>`. Numeric ids remain roadmap (the considered `R-` prefix was dropped to avoid breaking existing ids, links and memories). The roadmap × modifications frontier is 3 questions: does it fit in ~3 tasks? Does it fit in a card without a planning interview? Does it only touch existing contracts? Any "no" → roadmap; when in doubt, modification.

Only the human creates a modification (the agent proposes). Completed modification rows stay in the index (like epochs); it is the task rows that leave after valid memory (rule 17, no exception). `M-<n>` ids are never reused. The `weekly-review` proposes promotion to the roadmap when a modification swells (>~3 tasks or too old): open tasks conclude as `M-`; only the not-yet-tasked work migrates — kanban task ids are immutable.

**Rationale:** "continuous epoch that never completes" was the harness's most confusing concept; narrative (roadmap) and maintenance/emergency (modifications) are distinct natures and now have distinct documents, with the same kanban machine.

## Contracts

- [[WORKFLOW|WORKFLOW]] — *follow for yolo gates and per-scope merge*.
- [[specs/multi-agent-orchestration|Multi-agent orchestration]] — *follow for the yolo single gate*.
- [[specs/harness-lifecycle|Harness lifecycle]] — *follow for the cleanup rule extended to modifications*.
