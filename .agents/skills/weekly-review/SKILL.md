---
name: weekly-review
description: Periodic vault review - sweeps projects, epochs, modifications and tasks, flags what is stalled and proposes promotions or abandonments. Use when the user asks for a roadmap review or a vault overview.
---

# weekly-review

Generates a vault overview and proposes actions. Changes nothing beyond the report — decisions belong to the human.

**Delegate to subagents:** all the collection in step 2 — the main agent runs step 1's scripts and only consolidates the report.

## Procedure

1. **Scripts first:** run `scripts/pop_status.py` (kanban overview, blocked tasks, pending gates — 003, review/human in `005_closing`, `awaiting_merge`, >14 days) and `scripts/pop_validate.py` (limits, frontmatter and warnings). INBOX.md is Dataview, not a source.
   Then, **freshness of the installed harness**: for every project with `pop/.included-harness.json` (an `included` clone or an embedded repo of a `full-multi-repo`), run `python3 scripts/pop_install_included.py --check-fresh <dir>` — exit 0 is current, exit 1 is stale or unstamped. The **source is always the root PoP**: a project never fixes its harness by editing the local copy, it **reinstalls** with `python3 scripts/pop_install_included.py <dir>` (mirrors the managed set; the prune reaches only the previous install's inventory, so the project's own files in a managed directory stay). Always run it from the root PoP: from the installed copy the command refuses with exit 2. A stale target is a **high-priority** finding in the report — a one-command remedy, listed as such; use `--sha` to cite the source version.
2. **What the scripts don't cover → parallel subagents**, one per front, in **waves of 3-5**, each with a specific question and an answer ≤30 lines with a **source per finding** and a "Gaps / Not found" section (workers spawn no subagents):
   - **Drift in the installed harness:** the **whole** managed set — `.agents/skills/`, `pop/WORKFLOW.md`, `pop/TYPES.md`, `pop/_templates/`, `pop/scripts/` — of each project, including the embedded repos of `full-multi-repo` projects (`<project>/<repo>/`). Instrument: `--check-fresh` (step 1); when the stamp shows a difference, **detail it with `diff`** against the root source to say *what* diverged (old state machine, stale script, missing template). A project with no stamp, or with a `pop/WORKFLOW.md` of a different stage count, is severe drift. Divergence becomes a reinstall proposal, never a local patch.
   - **Project base files:** per project, measure `AGENTS.md` and `pop/PROJECT.md` (`wc -l`) against the cap — **~60 lines** for a project AGENTS.md, with the applications' DOX section as the declared exception (only they may exceed it, and only through DOX). Flag as a candidate for a **triggered pointer** every passage that narrates what already lives in [[WORKFLOW|WORKFLOW]], [[TYPES|TYPES]] or the root [[AGENTS|AGENTS]] rules (13 kanban, 17 memory, 20 human command) instead of linking to it. A cheap symptom: a reference to a nonexistent stage (`005_verifying`, `006_done`) — `grep` finds it and it proves the duplicated text rotted. This front **proposes** (file, lines, passages to replace with a link); it edits nothing.
   - **Indexes vs. reality:** status in the category INDEXes vs. actual activity in the kanban; **Aggregated repositories** (root INDEX) vs. actual clones/`.gitignore`.
   - **Orphaned worktrees:** each project's `pop/worktrees/` with content whose task is not in `004`/`005_closing` awaiting merge (the vault-root meta-project and not-yet-migrated projects: harness at the root, no `pop/`) — including the `<repo>/pop/worktrees/` inside the embedded repos of `full-multi-repo` projects.
   - **Outdated specs:** the `sync-specs` skill's audit (tasks in done whose specs weren't updated).
   - **DOX audit:** in application projects with a DOX tree ([[_templates/DOX|template]]), obsolete contracts (purpose/structure/flow changed without an update), dead links (laterals, skills, specs and indexes pointing to a nonexistent path) and blown caps (~60 lines, ~3 laterals, <7 references per contract).
   - **Note health:** orphan notes (no inbound wikilinks in the vault) and contradictions between notes/decisions and specs — reply ≤15 lines: candidates to link, merge or mark with `> Contradicts:`.
   - **Memory, roadmap and modifications health:** completed-task residue reported by `pop_validate`; memories over 2000 characters or repetitive/narrative candidates for [[.agents/skills/optimize-memory/SKILL|optimize-memory]]. Report only—never compact or delete during review.
   - **Stalled epochs:** "Abandon/pause if" conditions met in the epoch files; imported projects with Epoch 1 (Organization) open — since when and what is missing to release the gate.
   - **Swollen modifications:** a modification with more than ~3 open tasks or open for too long → proposal of promotion to a roadmap phase/epoch via `plan-roadmap` (open tasks conclude as `M-`; only the not-yet-tasked work migrates — frontier in [[AGENTS|AGENTS]]).
   - **Orphaned yolo:** external `develop` scopes stalled without their final automatic `develop` → `main` PR. Root-local PoP is exempt because it delivers directly to `main`.
3. **Consolidate:** the main agent only assembles the report from the scripts and the subagents' answers. Write it in the target's `notes/` (project: `pop/notes/`), or — if it covers the whole vault — in `REVIEW-YYYY-MM-DD.md` at the root, with:
   - **Waiting on you**: pending human gates and `open` questions in `open_questions/`, with link and since when.
   - **Stalled**: tasks/projects without movement, with a suggestion (resume, pause, abandon) and a one-line justification.
   - **Progress**: what moved since the last review (compare with the previous report, if any).
   - **Harness to reinstall**: targets stale in `--check-fresh`, with the exact reinstall command and what diverged.
   - **Proposals**: promotions of ideas to epoch, epochs ready to complete, modifications to promote to the roadmap, priority adjustments, drafts in `drafts/` ready to process (`new-project`/`import-project`).
4. Link the report in INBOX.md (new "Reviews" section if needed) so the human can find it.

## Cautions

- Report ≤150 lines; extra detail becomes a linked note.
- Do not move tasks or change statuses during the review — only propose.
- Remove review reports older than 3 months (or move them to an archive folder) when creating a new one.
