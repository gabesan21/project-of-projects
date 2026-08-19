---
author: user
date: 2026-08-18
---

# Harness decisions — 2026-08-18

## The PoP now has only two types

`included` becomes **`uni-repo`** and `full-multi-repo` becomes **`multi-repo`**. `default` and the old `multi-repo` (central kanban in the parent) cease to exist.

**Rationale:** four types multiplied combinations without adding expressiveness — every project reduces to "one repo that carries its harness" or "several repos, each with its own harness".

## `categories/` ends

Projects live in `projects/`, one folder per project; in a uni-repo the folder is the repository itself (the repo-less variant stays valid, versioned in the PoP).

**Rationale:** the category level added an index and a routing decision per project without paying off; the root INDEX becomes the vault's only project index.

## The multi-repo parent has no harness

Only `AGENTS.md`, `INDEX.md` (references the repos) and a general `ROADMAP.md`, reserved for cross-repo plans; at execution/planning time the epochs go into the repos' ROADMAPs. Each repo has its own kanban.

**Rationale:** a parent harness without a kanban was dead weight; whatever the parent tracked already lives, complete and standalone, in each repo.

## Total renaming, with no backwards compatibility

Artifacts, scripts, skills and templates that cite the old types are changed in the migration (`pop_install_included.py`, `included-manifest.json`, `.included-harness.json` included) — a one-time migration, with no dual-name support.

**Rationale:** keeping aliases for the old names would perpetuate two vocabularies for the same model; a single clean break keeps the harness unambiguous.

## Contracts

- [[TYPES|TYPES]] — *follow for the two-type model and the parent-without-harness anatomy*.
- [[AGENTS|AGENTS]] — *follow for the vault structure without categories and the single root index*.
