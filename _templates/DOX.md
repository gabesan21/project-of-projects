# DOX process — hierarchical agent context in the code

> PoP standard for **application** (programming) projects. **Self-contained** model, inspired by the open DOX framework (agent0ai/dox, MIT) — PoP does not depend on the original repository. Copy this entire section into the application project's AGENTS.md (it may exceed the ~150 lines to hold it); the child contracts live alongside the code.

## What it is

A tree of `AGENTS.md` files inside the code: the one at the code root is the **DOX rail** — rules for the whole project + high-level index; each relevant directory has its own, with local rules and an index of its own subtree. Each `AGENTS.md` is a **binding work contract for its subtree**: no blind edits, no stale documentation.

## Rules

1. **Before editing:** read the code's root AGENTS.md, identify **all** affected paths and **walk the tree** down to each edit location, reading every applicable AGENTS.md along the way. The walk can be delegated to a subagent that returns **only the rules applicable** to the task's paths — the executor receives the extract, not the tree.
2. **Local understanding:** any point in the code must be understandable by reading only the nearest AGENTS.md + all its parents above it. If it isn't, a contract is missing — create/complete the local one before editing.
3. **Conflicts:** the nearest document rules over local details; a child **never weakens** a parent's directive.
4. **Operational concision:** broad rules at the high levels, concrete detail in the children. Only what changes editing decisions — no prose. Cap: **~60 lines** per subtree contract; overflowed, the detail moves down into a child. Exception: a large-tree directory (many subfolders) may exceed it to hold the subtree's index — the exception covers the index, not prose.
5. **Mandatory review:** every relevant change requires reviewing the affected AGENTS.md files — update them when purpose, scope, responsibility, structure, flows, inputs, outputs or quality standards change.
6. **Closeout:** when finishing the work, re-check the changed paths, update the owning document and the affected parents, refresh the indexes, remove obsolete content and run the pertinent checks.
7. **Related contracts:** optional section in each contract with relative markdown links (`../services/payments/AGENTS.md`) to contracts of other subtrees that local decisions depend on — each link with a 1-line **trigger** (*when to follow it*). Max. **~3 laterals (ideally 0-2)** and **<7 total references** per contract (laterals + skills + children index); only a dependency that changes an editing decision (not every import); a link without a trigger doesn't count. Need more? A sign of coupling, or of routing that belongs in the parent's index. The walk becomes: vertical down to the edit location + the laterals whose trigger matches the task. The closeout (rule 6) also updates the laterals of the touched contracts.
8. **Subtree skills:** a contract may link project skills (`skills/`) **specific to that folder** — a procedure that changes how the subtree is edited (e.g. `migrations/` links the migration skill with the trigger "follow before creating/changing any migration"). Always a link with a trigger, never a copy of the content (copy = drift). **Workflow** skills (advance-task etc.) never go into a contract — they belong to the card's "Skills per stage" table: the card answers "how do I work this task"; the contract answers "what holds when editing this folder, whatever the task". Skill links count toward rule 7's reference cap.

## Initialization

Code without a DOX tree → recursive sweep and tree construction: root AGENTS.md with the general index and child contracts **only where the directory has ≥2 non-obvious conventions or has already caused a blind-edit error** — do not create empty AGENTS.md files "just in case". In an imported project (`import-project`), initialization is a task of Epoch 1 (Organization).

## In the PoP flow

- **002 (wargame):** the recon includes the AGENTS.md files applicable to the paths the task touches; the plan lists the contracts that will need updating.
- **004:** edit only after walking the tree; the changed AGENTS.md files go into the same worktree/PR as the task.
- **005:** verification checks that the affected contracts were updated — an implicit acceptance criterion of every application task.
- **Type `default` with an external repo that must stay clean of AI files:** decide with the user in the interview — commit the DOX tree to the repo (PoP default) or keep only the root contract in the project's AGENTS.md, inside PoP.
