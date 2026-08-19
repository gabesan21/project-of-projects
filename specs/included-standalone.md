---
id: included-standalone
project: pop
domain: harness
kind: contract
status: superseded
implementation: not_applicable
origin: "4.1"
created: 2026-07-13
updated: 2026-08-18
supersedes: []
superseded_by: unirepo-standalone
---

# Spec — Fully standalone included harness

## Contract

After an `included` repository is cloned and opened as the working directory, it provides the complete PoP harness without reading its parent vault.

## Expected behavior

- The clone can execute stages 001→`005_closing`, normal and yolo, using only versioned local files and declared external tools.
- `AGENTS.md`, `CLAUDE.md`, `.agents/skills/`, and `pop/` make every referenced instruction, command, template, gate, and skill locally available.
- `pop_install_included.py` uses `_templates/included-manifest.json` as the single package inventory and is safely repeatable.
- `pop/.included-harness.json` records the installed package; managed paths are refreshed while project-owned roadmap/specs/notes/memory/cards remain intact.
- Updating removes what the source retired, so a clone never keeps offering a template or script the flow dropped. The package propagates neither the parent's test suite nor its bytecode.
- **Pruning is bounded by the previous install's inventory**, recorded under `installed` in the marker: a managed folder is not an exclusive folder, and a project's own files living inside one are never candidates. With no previous inventory, nothing is pruned.
- Every install stamps the source's `content_sha` into the target, and a command recomputes it and **fails closed** when the target fell behind. Without the stamp, a clone parked on an old version of the flow is indistinguishable from a current one. The aggregating vault's validator treats a stale or unstamped target as a violation, with the fix command in the message. The installed copy is not the source and refuses to answer about freshness.
- Validation that compares the scope label (`project:` in memory and specs) demands equality only where sibling projects exist; in a standalone clone the scope is the root itself and the label inherited from the parent vault is not reproducible, so there the field need only be filled.
- Internal wikilinks resolve inside the clone and never require `categories/<category>/<project>` from a parent vault.
- Every embedded repo in `full-multi-repo` receives the same standalone contract plus optional local membership links.

## Errors and limits

Missing manifest entries, scripts, skills, anatomy markers, or locally resolvable links fail standalone validation. The installer never copies personal projects, populated notes, research, questions, credentials, worktrees, or repository content.

## Conformance

- [x] Manifest closure is audited by `pop_install_included.py --audit-manifest`.
- [x] Installation and real-clone operation are covered by the strict-anatomy and included tests.
- [x] `pop_validate.py --standalone` fails closed on an incomplete package.
