# Spec — <contract/theme name>

> Blockquotes are filling instructions — **delete them when filling**.

- **Project:** [[categories/<category>/<project>/pop/PROJECT|<Project name>]]
- **Epoch/Phase:** [[categories/<category>/<project>/pop/roadmap/<n>-<slug>|Phase <n>.<m>]]
- **Status:** draft | approved | implemented | obsolete
- **Created:** YYYY-MM-DD
- **Updated:** YYYY-MM-DD

## Contract

Objective description of durable behavior or theme. One spec answers one question; split it if it answers two.

## Expected behavior

- Given <state/input>, when <event>, then <observable result>.

## Invariants

- <rule that remains true under any implementation>.

## Interfaces

> Record only interfaces promised to consumers: payloads, schemas, commands, events, states or public signatures. Code only when it is itself the contract.

- **Input:** <format, constraints and minimal example if needed>.
- **Output:** <format and guarantees>.
- **Compatibility:** <affected versions or consumers>.

## Errors and limits

- **<condition>:** <observable error/state and expected behavior>.
- **Limit:** <relevant constraint>.

## Conformance criteria

- [ ] <objectively verifiable behavior or invariant>.

## Out of scope

- <what does not belong here and where it is covered>.

## Open questions

- <unanswered question; remove when empty>.

## Related references

- [[categories/<category>/<project>/pop/specs/<other-spec>|<other-spec>]] — *follow if <condition>*.
- [`<subtree>/AGENTS.md`](../<path-in-repo>/AGENTS.md) — *follow before changing <area>*.

> Do not record internal solutions, edit sequences, reasoning or pseudocode. Change strategy belongs in the plan; reusable procedures belong in a skill.
