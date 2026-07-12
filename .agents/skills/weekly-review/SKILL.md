---
name: weekly-review
description: Periodic vault review - sweeps projects, epochs and tasks, flags what is stalled and proposes promotions or abandonments. Use when the user asks for a roadmap review or a vault overview.
---

# weekly-review

Generates a vault overview and proposes actions. Changes nothing beyond the report — decisions belong to the human.

**Delegate to subagents:** all the collection in step 2 — the main agent runs step 1's scripts and only consolidates the report.

## Procedure

1. **Scripts first:** run `scripts/pop_status.py` (kanban overview: tasks per stage/project, blocked ones, pending gates — 003, critical in 005, `awaiting_merge`, stalled for >14 days) and `scripts/pop_validate.py` (limit violations: 144/600 chars, ~150 lines, frontmatter, `stage` vs folder; warnings: orphan worktrees, broken wikilinks). INBOX.md is Dataview, not a source.
2. **What the scripts don't cover → parallel subagents**, one per front, in **waves of 3-5** (6 fronts → 2 waves), each with a specific question and an answer ≤30 lines with a **source per finding** and a "Gaps / Not found" section (workers spawn no subagents):
   - **Drift in copied skills:** `diff` between each project's `.agents/skills/` — including the embedded repos of `full-multi-repo` projects (`project/<repo>/.agents/skills/`) — and the root core skills — divergence becomes a sync proposal.
   - **Indexes vs. reality:** status in the category INDEXes vs. actual activity in the kanban; **Aggregated repositories** (root INDEX) vs. actual clones/`.gitignore`.
   - **Orphaned worktrees:** `worktrees/` with content whose task is not in `004`/`005`/`006` awaiting merge — including the `worktrees/` inside the embedded repos of `full-multi-repo` projects.
   - **Outdated specs:** the `sync-specs` skill's audit (tasks in done whose specs weren't updated).
   - **Note health:** orphan notes (no inbound wikilinks in the vault) and contradictions between notes/decisions and specs — reply ≤15 lines: candidates to link, merge or mark with `> Contradicts:`.
   - **Stalled epochs:** "Abandon/pause if" conditions met in the epoch files; imported projects with Epoch 1 (Organization) open — since when and what is missing to release the gate.
3. **Consolidate:** the main agent only assembles the report from the scripts and the subagents' answers. Write it in the target's `notes/`, or — if it covers the whole vault — in `REVIEW-YYYY-MM-DD.md` at the root, with:
   - **Waiting on you**: pending human gates and `open` questions in `open_questions/`, with link and since when.
   - **Stalled**: tasks/projects without movement, with a suggestion (resume, pause, abandon) and a one-line justification.
   - **Progress**: what moved since the last review (compare with the previous report, if any).
   - **Proposals**: promotions of ideas to epoch, epochs ready to complete, priority adjustments, drafts in `drafts/` ready to process (`new-project`/`import-project`).
4. Link the report in INBOX.md (new "Reviews" section if needed) so the human can find it.

## Cautions

- Report ≤150 lines; extra detail becomes a linked note.
- Do not move tasks or change statuses during the review — only propose.
- Remove review reports older than 3 months (or move them to an archive folder) when creating a new one.
