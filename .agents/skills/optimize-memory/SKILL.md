---
name: optimize-memory
description: Compacts PoP memories without losing identity, evidence, chronology, or critical decisions. Use on explicit request, overlong memories, or weekly-review candidates.
---

# optimize-memory

Reduce each ledger without turning `memory/` into a changelog or erasing proof. The unit remains **one file per task**: never merge, delete, or rename memories.

## Preflight and irreducible data

For every file, inventory path, `task`, `project`, `started`, `finished`, `commit`, `pr`, event order, and durable decisions. Missing required fields or ambiguous chronology is **BLOCKED**—do not infer.

Preserve all frontmatter; task identity; dates; commit and PR (including an explicit empty value); the order of start, delivery, verification, integration/PR, and finish; delivered result; final verification; contract-changing deviations; critical decisions and rationale; and valid triggered links.

A critical decision constrains future behavior or records a human choice, security, compatibility, ownership, migration, irreversibility, or approved deviation. When uncertain, preserve it.

## What may be compacted

- Repeated plan text, edit steps, and trial-and-error narrative.
- Long file lists that one subtree plus a sentence can replace.
- Duplicate evidence when the final command/result preserves proof.
- Context already held by a linked spec/decision, retaining one sentence and its trigger.

Write short facts in chronological order. Do not add history, reinterpret decisions, or replace pointers with prose.

## Safe procedure

1. Produce a candidate using [[_templates/MEMORY|the memory template]].
2. Compare it with the preflight inventory; any irreducible loss rejects it.
3. Confirm ≤2000 characters and `YYYY-MM-DD` dates.
4. Validate wikilinks and run `python3 scripts/pop_validate.py`.
5. Review each diff; on failed preservation, restore the original and report **BLOCKED**.

Report paths, before/after character counts, preserved fields/decisions, and validations. If no material safe gain exists, leave the file unchanged. Do not edit specs, decisions, roadmaps, cards, code, or Git; weekly review only identifies candidates unless the human authorizes compaction.
