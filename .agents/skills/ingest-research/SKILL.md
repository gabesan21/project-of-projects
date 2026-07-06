---
name: ingest-research
description: Ingests a deep-research result (or external source) delivered by the user - immutable raw source in raw/, short synthesis with triggered links and a contradiction check against specs, decisions and notes. Use when the user deposits a research result or asks to process a new source.
---

# ingest-research

**Principle: knowledge that arrives integrates into the vault, it doesn't just pile up.** The source becomes a synthesis linked to what it affects, and contradiction with what is already written stays visible — never silent. (pattern: LLM-maintained wiki — raw sources → synthesized, interlinked notes)

**Delegate to subagents:** the reading of the entire raw source (rule 18) — the main agent positions files, updates indexes and decides what to propose.

## Folder convention

- `researches/<topic>/raw/` — the **raw, immutable** source, as the user delivered it. Never edit it; exempt from the ~150-line limit and from the wikilink lint.
- `researches/<topic>/<topic>.md` — the agent's synthesis (≤150 lines), with triggered links to what the finding affects.

## Procedure

1. **Position the raw source:** save/move the delivered material to `researches/<topic>/raw/` (topic in kebab-case; create the folder if the research is new).
2. **Synthesis subagent** receives: (a) the path to the raw source; (b) the corresponding section of RESEARCHES.md (especially the "Feeds:"); (c) the list of specs/decisions/notes related to the topic. It returns ≤60 lines: central findings, actionable recommendations and — mandatory — the answer to "does any finding **contradict** an existing spec, decision or note? which one, and why".
3. **Write the synthesis** in `researches/<topic>/<topic>.md` from the answer. A contradiction becomes a `> Contradicts: [[target]] — <why, in 1 line>` line in the synthesis **and** an item in the "Open" section of the affected spec (same mechanism as `sync-specs` in 004).
4. **Update the index:** in the project's RESEARCHES.md, if it exists, status → `delivered` with a link to the **synthesis** (not to the raw source).
5. **Propose, don't apply:** list to the user the concrete updates the finding suggests — the roadmap changes via `plan-roadmap`, a spec via `write-spec`. Ingestion prepares the decision; it changes neither roadmap nor spec.

## Cautions

- One ingestion per source: several sources delivered at once → process one at a time (each synthesis stays traceable to its raw source).
- Does a synthesis for the topic already exist? **Update it** with the new source instead of creating another — and flag it if the new source contradicts the previous synthesis.
- Only `raw/` is exempt from the vault rules; everything the agent writes follows the limits and the link convention normally.
