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

## Import-project without mandatory specs

Epoch 1 (Organization) of an imported project becomes the project map (the DOX tree in applications; the recon map consolidated in `PROJECT.md` outside them) + skills + research + notes, and the ROADMAP is born containing only it — the future is planned by `plan-roadmap` when Epoch 1 concludes, not during the import. Specs leave Epoch 1 and are born **work-driven**: a task that touches a topic with no spec → the agent proposes creating it (`write-spec`), the user decides; if they don't want it, it isn't done. In a new project (`new-project`), a spec is design and stays valid from the start.

**Rationale:** a spec of an existing project is reverse engineering — expensive and error-prone without supervision (especially in large repos), and a wrong spec is worse than no spec.

## Contracts

- [[WORKFLOW|WORKFLOW]] — *follow for the current-branch integration and the suggested final PR*.
- [[AGENTS|AGENTS]] — *follow for rule 16 (worktrees and ownership)*.
- [[specs/harness-lifecycle|Harness lifecycle]] — *follow for the external-yolo delivery invariant*.
- [[.agents/skills/import-project/SKILL|import-project]] — *follow for the spec-less Epoch 1 and work-driven specs*.
