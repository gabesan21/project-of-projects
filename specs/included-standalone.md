---
id: included-standalone
project: pop
domain: harness
kind: contract
status: active
implementation: implemented
origin: "4.1"
created: 2026-07-13
updated: 2026-07-21
supersedes: []
superseded_by:
---

# Spec — Fully standalone included harness

## Contract

After an `included` repository is cloned and opened as the working directory, it provides the complete PoP harness without reading its parent vault.

## Expected behavior

- The clone can execute stages 001→006, normal and yolo, using only versioned local files and declared external tools.
- `AGENTS.md`, `CLAUDE.md`, `.agents/skills/`, and `pop/` make every referenced instruction, command, template, gate, and skill locally available.
- `pop_install_included.py` uses `_templates/included-manifest.json` as the single package inventory and is safely repeatable.
- `pop/.included-harness.json` records the installed package; managed paths are refreshed while project-owned roadmap/specs/notes/memory/cards remain intact.
- Internal wikilinks resolve inside the clone and never require `categories/<category>/<project>` from a parent vault.
- Every embedded repo in `full-multi-repo` receives the same standalone contract plus optional local membership links.

## Errors and limits

Missing manifest entries, scripts, skills, anatomy markers, or locally resolvable links fail standalone validation. The installer never copies personal projects, populated notes, research, questions, credentials, worktrees, or repository content.

## Conformance

- [x] Manifest closure is audited by `pop_install_included.py --audit-manifest`.
- [x] Installation and real-clone operation are covered by the strict-anatomy and included tests.
- [x] `pop_validate.py --standalone` fails closed on an incomplete package.
