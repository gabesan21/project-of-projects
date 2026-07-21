---
id: frontend-skills
project: pop
domain: frontend
kind: contract
status: active
implementation: implemented
origin: "5.1"
created: 2026-07-14
updated: 2026-07-21
supersedes: []
superseded_by:
---

# Spec — Vendored frontend skills

## Contract

The public PoP distributes the licensed frontend/UI/UX skills listed in `AGENTS.md` as faithful upstream copies, plus its own `ui-change` and `ui-review` workflow pair.

## Invariants

- Vendored skills remain byte-identical to their upstream source; updates are re-vendored, never locally patched.
- Every skill has its own AGENTS table entry with source and license.
- Skills without a declared redistribution license are not vendored in the public repository; `excalidraw-diagram` remains an optional credited link.
- Tool-specific skill directories are never the source of truth.
- `ui-change` and `ui-review` are PoP-owned workflow skills and may evolve with the harness.

## Conformance

- [x] Public inventory, attribution, and licenses are present.
- [x] Included packaging copies only the core workflow subset declared by the manifest.
