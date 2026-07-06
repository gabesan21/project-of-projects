---
name: weekly-review
description: Periodic vault review - sweeps projects, epochs and tasks, flags what is stalled and proposes promotions or abandonments. Use when the user asks for a roadmap review or a vault overview.
---

# weekly-review

Generates a vault overview and proposes actions. Changes nothing beyond the report — decisions belong to the human.

## Procedure

1. Collect the state:
   - Tasks per stage: `grep -r "^stage:" */*/kanban --include="*.md"` (card frontmatter).
   - Pending gates: cards in `003_human_approval`, critical ones in `005_verifying`, `blocked: true` and `awaiting_merge: true` (PRs waiting for human merge) — grep the frontmatter; INBOX.md is Dataview, not a source.
   - Stalled tasks: `updated:` more than 14 days ago and not in `006_done`.
   - Projects: status in the category INDEXes vs. actual activity in the kanban; repos in the **Aggregated repositories** list (root INDEX) vs. actual clones/`.gitignore`.
   - Outdated specs: run the `sync-specs` skill's audit (tasks in done whose specs weren't updated).
   - Drift in copied skills: in **every** project, `diff` between the project's `.agents/skills/` and the root core skills — divergence becomes a sync proposal.
   - Orphaned worktrees: `worktrees/` with content whose task is not in `004`/`005`/`006` awaiting merge.
   - Epoch abandon/pause conditions (the "Abandon/pause if" line in the epoch files): any met? → proposal to pause/abandon.
   - Imported projects with Epoch 1 (Organization) open: since when, and which specs/skills are missing to release the gate.
2. Write the report in the target's `notes/`, or — if it covers the whole vault — in `REVIEW-YYYY-MM-DD.md` at the root, with:
   - **Waiting on you**: pending human gates, with link and since when.
   - **Stalled**: tasks/projects without movement, with a suggestion (resume, pause, abandon) and a one-line justification.
   - **Progress**: what moved since the last review (compare with the previous report, if any).
   - **Proposals**: promotions of ideas to epoch, epochs ready to complete, priority adjustments.
3. Link the report in INBOX.md (new "Reviews" section if needed) so the human can find it.

## Cautions

- Report ≤150 lines; extra detail becomes a linked note.
- Do not move tasks or change statuses during the review — only propose.
- Remove review reports older than 3 months (or move them to an archive folder) when creating a new one.
