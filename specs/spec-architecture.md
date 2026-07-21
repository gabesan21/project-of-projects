---
id: spec-architecture
project: pop
domain: harness
kind: contract
status: active
implementation: implemented
origin: "6.1"
created: 2026-07-20
updated: 2026-07-21
supersedes: []
superseded_by:
---

# Spec — Spec architecture

## Contract

A `specs/` collection holds machine-readable current contracts that remain discoverable as a project grows. A spec answers one durable question; the roadmap plans, the card coordinates change, and `memory/` proves what happened.

Canonical frontmatter contains `id`, `project`, `domain`, `kind`, `status`, `implementation`, `origin`, `created`, `updated`, `supersedes`, and `superseded_by`. Enums are `kind: contract|overview`, `status: draft|active|superseded`, and `implementation: planned|partial|implemented|not_applicable`.

## Invariants

- Creating `specs/INDEX.md` opts the entire collection into the canonical format atomically.
- Every draft/active contract is reachable directly from the index or through one indexed domain overview.
- The tree is at most `specs/<domain>/<file>.md`; `overview.md` maps boundaries and triggered links without repeating requirements.
- IDs are unique; `project` matches the scope label; a nested contract's `domain` matches its folder.
- Supersession is reciprocal: old and replacement specs point to each other.
- Specs contain current behavior, invariants, interfaces, errors, and criteria—not task history or implementation reasoning.

## Errors and validation

Malformed fields, invalid enums/dates, duplicate IDs, deep nesting, unreachable current specs, and non-reciprocal supersession are violations. Legacy collections without `INDEX.md` remain accepted until migrated atomically.

## Conformance

- [x] [[_templates/SPEC|SPEC]] emits canonical metadata.
- [x] [[.agents/skills/sync-specs/SKILL|sync-specs]] defines lifecycle and discovery.
- [x] `scripts/pop_validate.py` and `scripts/tests/test_spec_validation.py` enforce the contract.
