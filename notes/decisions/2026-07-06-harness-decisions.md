---
author: agent
created: 2026-07-06
---

# Harness decisions — 2026-07-06

- **Run until the human gate:** one run = up to the next human gate (approval in 003; `critical: true` in 005; a `(user)` item; `blocked: true`; merge round in 006) — supersedes "Single stage per invocation" from [[notes/decisions/2026-07-05-harness-decisions|2026-07-05]]. The main agent becomes the **orchestrator** (card, gates, transitions) and each work stage runs in a dedicated subagent with only that stage's skill: planner in 002, executor in 004, verifier in 005 (verifier ≠ executor by design); 001 and 006 stay with the orchestrator — detail in [[WORKFLOW|WORKFLOW]].
- **Delegation by default:** broad context reading (recon, audits, sweeps, DOX tree walks, skill diffs) never runs in the main agent's window — it goes to a subagent with (a) a specific question, (b) the relevant skill/section, (c) a response format with a cap (e.g. ≤30 lines). Rule 18 of [[AGENTS|AGENTS]].
- **Links with a trigger:** in agent-facing navigation sections (the card's Links, related specs, memory, learnings, DOX contracts), every link carries 1 line saying **when** to follow it — convention recorded in [[AGENTS|AGENTS]].
- **Python scripts in `scripts/`:** CLI in Python ≥3.9, **stdlib only** and `pathlib` (agent-agnostic, cross-platform): `pop_status`, `pop_move`, `pop_validate`, `pop_task`, `pop_worktree` — agent sweeps become 1 command; reading (`pop_status`, `pop_validate`) implemented first.
- **Context protocol:** standard section in the project AGENTS.md ([[_templates/AGENTS-PROJECT|template]]): start from the card/plan and read only what they list; gap → subagent with a specific question; stop once you know "what changes and where"; an unresolved doubt becomes RECON NEEDED or `blocked:`; specs and memory before archaeology in git/code. Complement: the "Minimal executor context" section in [[_templates/TASK-PLAN|TASK-PLAN]].
- **DOX calibrated:** cap of **~60 lines** per contract (exception: a subtree with a large tree, covering only the index, not prose); the tree walk is delegable to a subagent; a child contract only with ≥2 non-obvious conventions or a prior blind-edit error; optional **Related contracts** section with lateral links with a trigger (max ~5, only dependencies that change edit decisions, updated at closeout).
