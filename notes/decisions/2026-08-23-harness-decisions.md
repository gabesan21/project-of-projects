---
author: user
date: 2026-08-23
---

# Harness decisions — 2026-08-23

## External yolo without a fixed `develop`

The yolo task's worktree now starts from the repo's **current working branch** (no longer always from `develop`), resolved at worktree-add time via `git branch --show-current`, and the mechanical `005_closing` integration merges `task/<id>` into that same current branch. A detached HEAD aborts.

**Rationale:** hardcoding `develop` forced every external yolo repo into a branching model it may not follow; the current working branch is where the human is actually working, so the task branch should start and land there.

## Final PR on request only

The agent no longer automatically opens the final PR when the yolo scope closes; it **suggests** the PR from the working branch to `main` and only creates it (`pop_delivery.py scope-pr`, with `--base` defaulting to `main`) on the user's explicit request. The merge stays human.

**Rationale:** an automatic PR made the agent open a human-facing artifact on its own; suggesting keeps the scope close visible without acting in the human's place.

## Contracts

- [[WORKFLOW|WORKFLOW]] — *follow for the current-branch integration and the suggested final PR*.
- [[AGENTS|AGENTS]] — *follow for rule 16 (worktrees and ownership)*.
- [[specs/harness-lifecycle|Harness lifecycle]] — *follow for the external-yolo delivery invariant*.
