# weekly-review — fronts for whoever hosts other scopes

> This file is **not installed** into scopes that receive the harness (`exclude_files` in the [[_templates/included-manifest|manifest]]). It only exists where there are child projects: if you are reading it, the current scope is the harness origin. An installed scope does not have this file and therefore does not have these fronts — that is how the boundary holds without relying on the agent remembering it.

Run these fronts **in addition** to the ones in [[.agents/skills/weekly-review/SKILL|SKILL.md]], in the same format (one subagent per front, answer ≤30 lines, a source per finding).

## Additional fronts

- **Freshness of the installed harness:** for every target with `pop/.included-harness.json` (an `included` clone or an embedded repo of a `full-multi-repo`), run `python3 scripts/pop_install_included.py --check-fresh <dir>` — exit 0 is current, exit 1 is stale or unstamped. The comparison is **always** made from here: the target reports only its own version. Stale is a **high-priority** finding — a one-command remedy (`python3 scripts/pop_install_included.py <dir>`, which mirrors the managed set; the prune reaches only the previous install's inventory, so the project's own files in a managed directory stay). Use `--sha` to cite the origin version.
- **Boundary of the managed set:** `python3 scripts/pop_install_included.py --audit-boundary`. A failure means the harness went back to describing this hosting scope inside the material that travels to the children — the origin of every context mix-up in a child project. The fix is rewriting the text or dropping the file from the package via `exclude_files`, never relaxing the guard.
- **Drift in the installed harness:** when the stamp shows a difference, **detail it with `diff`** against the origin to say *what* diverged (old state machine, stale script, missing template). A target with no stamp, or with a `pop/WORKFLOW.md` of a different stage count, is severe drift. Divergence becomes a reinstall proposal, never a local patch.
- **Indexes vs. reality:** status in the category INDEXes vs. actual activity in each project's kanban; **Aggregated repositories** (root INDEX) vs. actual clones and `.gitignore`.
- **Stalled projects:** projects with no kanban movement, with a suggestion (resume, pause, abandon).
- **Pending drafts:** files in `drafts/new/` and `drafts/import/` ready to become a project (`new-project` / `import-project`).

## Where to write

Report for the whole set: `REVIEW-YYYY-MM-DD.md` at the root, linked in the INBOX's **Reviews** section. A report for one specific project still goes to **that** project's `pop/notes/` — and in that case the review must be run from inside it, not from here.
