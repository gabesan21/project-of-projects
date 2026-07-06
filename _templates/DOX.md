# DOX process — hierarchical agent context in the code

> PoP standard for **application** (programming) projects. **Self-contained** model, inspired by the open DOX framework (agent0ai/dox, MIT) — PoP does not depend on the original repository. Copy this entire section into the application project's AGENTS.md (it may exceed the ~150 lines to hold it); the child contracts live alongside the code.

## What it is

A tree of `AGENTS.md` files inside the code: the one at the code root is the **DOX rail** — rules for the whole project + high-level index; each relevant directory has its own, with local rules and an index of its own subtree. Each `AGENTS.md` is a **binding work contract for its subtree**: no blind edits, no stale documentation.

## Rules

1. **Before editing:** read the code's root AGENTS.md, identify **all** affected paths and **walk the tree** down to each edit location, reading every applicable AGENTS.md along the way.
2. **Local understanding:** any point in the code must be understandable by reading only the nearest AGENTS.md + all its parents above it. If it isn't, a contract is missing — create/complete the local one before editing.
3. **Conflicts:** the nearest document rules over local details; a child **never weakens** a parent's directive.
4. **Operational concision:** broad rules at the high levels, concrete detail in the children. Only what changes editing decisions — no prose.
5. **Mandatory review:** every relevant change requires reviewing the affected AGENTS.md files — update them when purpose, scope, responsibility, structure, flows, inputs, outputs or quality standards change.
6. **Closeout:** when finishing the work, re-check the changed paths, update the owning document and the affected parents, refresh the indexes, remove obsolete content and run the pertinent checks.

## Initialization

Code without a DOX tree → recursive sweep and tree construction: root AGENTS.md with the general index and child contracts **wherever a local rule is worth it** — do not create empty AGENTS.md files "just in case". In an imported project (`import-project`), initialization is a task of Epoch 1 (Organization).

## In the PoP flow

- **002 (wargame):** the recon includes the AGENTS.md files applicable to the paths the task touches; the plan lists the contracts that will need updating.
- **004:** edit only after walking the tree; the changed AGENTS.md files go into the same worktree/PR as the task.
- **005:** verification checks that the affected contracts were updated — an implicit acceptance criterion of every application task.
- **Type `default` with an external repo that must stay clean of AI files:** decide with the user in the interview — commit the DOX tree to the repo (PoP default) or keep only the root contract in the project's AGENTS.md, inside PoP.
