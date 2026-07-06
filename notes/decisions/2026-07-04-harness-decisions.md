---
author: agent
created: 2026-07-04
---

# Harness decisions — 2026-07-04

- **INBOX via Dataview:** queries over the cards' frontmatter — no manual synchronization (requires the Dataview plugin in Obsidian; agents locate gates by grepping `stage:`).
- **WIP limit:** max. **3** tasks in `004_processing` per project (soft rule — see [[WORKFLOW|WORKFLOW]]).
- **Blocked tasks:** `blocked: true` + `blocked_reason:` in the card's frontmatter; they appear in the INBOX.
- **Derived status:** a phase is completed when all its tasks are in `006_done`; an epoch when all its phases complete — updated at stage 006.
- **Periodic review:** the `weekly-review` skill, run manually or by a scheduled routine of the user's tool.
- **Git:** repository initiated on 2026-07-04; see rule 15 of [[AGENTS|AGENTS]].
- **Validation:** the agent's own responsibility (rule 14 of [[AGENTS|AGENTS]]), no tool-specific hooks — keeps the vault agnostic.
- **Supervised execution:** no change to the real project outside the kanban (rule 13 of [[AGENTS|AGENTS]]) — the human gate at 003 is the only path for the agent to touch `project/`.
