---
name: weekly-review
description: Periodic review of the current scope - sweeps epochs, modifications and tasks, flags what is stalled and proposes promotions or abandonments. Use when the user asks for a roadmap review or an overview of the work.
---

# weekly-review

Generates an overview **of the current scope** and proposes actions. Changes nothing beyond the report — decisions belong to the human.

**The target is always the current scope** ("Current scope" section of [[WORKFLOW|WORKFLOW]]): the root holding the `AGENTS.md` you are reading. "Overview" never means leaving it. If an `origin-scope.md` sits next to this file, the scope hosts others and gains the extra fronts described there; if it does not exist, those fronts **do not apply** — do not look for them and do not invent them.

**Delegate to subagents:** all the collection in step 2 — the main agent runs step 1's scripts and only consolidates the report.

## Procedure

1. **Scripts first:** run `scripts/pop_status.py` (kanban overview, blocked tasks, pending gates — 003, review/human in `005_closing`, `awaiting_merge`, >14 days) and `scripts/pop_validate.py` (limits, frontmatter and warnings). INBOX.md is Dataview, not a source.
   **Harness version:** `python3 scripts/pop_install_included.py --check-fresh .` reports the version installed here. Comparing it against the origin is the job of whoever installed it — it is not a finding of this review and it never justifies going looking for the origin.
2. **What the scripts don't cover → parallel subagents**, one per front, in **waves of 3-5**, each with a specific question and an answer ≤30 lines with a **source per finding** and a "Gaps / Not found" section (workers spawn no subagents):
   - **Base files:** measure `AGENTS.md` and `pop/PROJECT.md` (`wc -l`) against the **~60 line** cap for the project AGENTS.md, with the applications' DOX section as the declared exception. Flag as a candidate for a **triggered pointer** every passage that narrates what already lives in [[WORKFLOW|WORKFLOW]] instead of linking to it. A cheap symptom: a reference to a nonexistent stage (`005_verifying`, `006_done`) — `grep` finds it and it proves the duplicated text rotted. This front **proposes** (file, lines, passages to replace with a link); it edits nothing.
   - **Orphaned worktrees:** `pop/worktrees/` with content whose task is not in `004`/`005_closing` awaiting merge.
   - **Outdated specs:** the `sync-specs` skill's audit (tasks in done whose specs weren't updated).
   - **DOX audit:** in an application with a DOX tree ([[_templates/DOX|template]]), obsolete contracts (purpose/structure/flow changed without an update), dead links and blown caps (~60 lines, ~3 laterals, <7 references per contract).
   - **Note health:** orphan notes (no inbound wikilinks in the scope) and contradictions between notes/decisions and specs — reply ≤15 lines: candidates to link, merge or mark with `> Contradicts:`.
   - **Memory, roadmap and modifications health:** completed-task residue reported by `pop_validate`; memories over 2000 characters or repetitive/narrative candidates for [[.agents/skills/optimize-memory/SKILL|optimize-memory]]. Report only — never compact or delete during review.
   - **Stalled epochs:** "Abandon/pause if" conditions met in the epoch files; Epoch 1 (Organization) still open — since when and what is missing to release the gate.
   - **Swollen modifications:** a modification with more than ~3 open tasks or open for too long → proposal of promotion to a roadmap phase/epoch via `plan-roadmap` (open tasks conclude as `M-`; only the not-yet-tasked work migrates — frontier in [[AGENTS|AGENTS]]).
   - **Orphaned yolo:** external `develop` scopes stalled without their final automatic `develop` → `main` PR. A local scope is exempt because it delivers directly to `main`.
3. **Consolidate:** the main agent only assembles the report from the scripts and the subagents' answers. Write it in the current scope's `pop/notes/` (`notes/` when the harness lives at the root itself), with:
   - **Waiting on you**: pending human gates and `open` questions in `open_questions/`, with link and since when.
   - **Stalled**: tasks without movement, with a suggestion (resume, pause, abandon) and a one-line justification.
   - **Progress**: what moved since the last review (compare with the previous report, if any).
   - **Proposals**: promotions of ideas to epoch, epochs ready to complete, modifications to promote to the roadmap, priority adjustments.
4. Link the report in INBOX.md ("Reviews" section) so the human can find it.

## Cautions

- Report ≤150 lines; extra detail becomes a linked note.
- Do not move tasks or change statuses during the review — only propose.
- Remove review reports older than 3 months (or move them to an archive folder) when creating a new one.
- A finding that could only exist outside the scope does not enter the report: it becomes a question in `open_questions/`, or it does not exist.
