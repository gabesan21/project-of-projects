---
id: multi-agent-orchestration
project: pop
domain: harness
kind: contract
status: active
implementation: implemented
origin: "4.2"
created: 2026-07-20
updated: 2026-08-10
supersedes: []
superseded_by:
---

# Spec — Multi-agent kanban orchestration

## Contract

There is no `pop-orchestrator` custom agent. The native main session receives its contract from `AGENTS.md` plus `advance-task`, operates delegation-first, and retains only routing, gates, transitions, and integration. Direct work is limited to a small/simple action below the delegation floor.

It delegates to six canonical specialists: `pop-planner`, `pop-recon`, `pop-execution-orchestrator`, `pop-executor`, `pop-judge-dredd`, and `pop-phase-verifier`. Model and effort are fixed properties of each runtime-native definition. Task `size` limits scope, front count, and depth; it never selects a model, effort, or agent.

## Authorization envelope and context acquisition

The envelope is a semantic contract, not a runtime schema. It identifies role, task/stage/round, input paths, `may_read`, `owns`, `must_not_edit`, web and skills, `depends_on`, `expected_input`, applicable gate/delta, and required output with artifact/format, cap, evidence, and status.

`owns` authorizes only writing; `may_read` authorizes only reading; deny overrides allow. An absent, inaccessible, or incompatible path returns `BLOCKED` without acquiring neighboring context or creating the dependency.

The envelope never embeds card, plan, front, spec, diff, or evidence content as a substitute for its source. Each specialist resolves only paths needed for its own output and validates identity, state, and dependencies before acting. Re-entry receives the delta and affected paths; fronts declared intact stay outside write and re-execution.

When a runtime cannot reliably enforce named nested-child allowlists, dispatch is flattened: planner/coordinator returns a child request/envelope, the main session spawns that specialist directly, and returns only the result path to the consumer. The main session never retells or interprets the substantive result.

## Roles

| Role | Trigger | Output | Key boundary |
|------|---------|--------|--------------|
| `pop-planner` | 002 and plan-defect re-entry | recon request when needed; then `.plan.md` ≤80 lines plus one ≤50-line slice per delegated front | writes only plan/subtasks; never executes, judges, integrates, or uses web |
| `pop-recon` | concrete question above the direct-reading floor | concise found/inferred/not-found report with path/line evidence | read-only except an authorized report; never plans, implements, judges, or uses web |
| `pop-execution-orchestrator` | 004 with DAG, multiple skills, or multiple write sets | executor requests plus checked wave/order/scope evidence | coordinates only; never implements, invokes children itself, judges, or integrates |
| `pop-executor` | cohesive 004 front, specialist front, repair, or delta re-entry | artifact/diff in `owns` plus inspection evidence | never reads neighboring fronts, integrates, moves cards, or judges |
| `pop-judge-dredd` | critical-yolo 003 and act 1 of every yolo 005 | `.verify.md` ≤80 lines; valid memory on 005 approval | judges only; never implements or dispatches its fix, integrates, moves cards, or uses web |
| `pop-phase-verifier` | 004 of the final phase-verification task | suite/fixes in `owns` plus run and criterion evidence | tests/fixes only within the phase; never reopens closed tasks, judges, or integrates |

## Expected behavior

- 002 always runs in a separate planner context and persists objective, strategy, fronts, dependencies, contracts, material risks, criteria, and evidence sources.
- A cohesive 004 front goes directly to one executor. Only a DAG, multiple skills, or multiple write sets receive the execution coordinator.
- Parallel fronts use isolated branches/worktrees; only the main session validates scope and integrates.
- 005 uses exactly one fresh `pop-judge-dredd` per yolo round. `L`/`critical` changes review depth, never model, effort, role, or judge count.
- Judge Dredd reads the original request, contracts, integrated diff, and evidence. Ordinary tests are `verify: phase` criteria run once by `pop-phase-verifier`, not rerun by the judge.
- Outside yolo there is no agentic reviewer: the human PR is the gate, and a local scope with no PR has no verification gate.
- Every return names a classified delta (`lacuna | premissa | execucao`), affected criteria/fronts, and intact fronts. Re-entry and rereview are differential unless a premise invalidates the surface.
- Yolo schedules waves of at most three independent tasks; delivery/close-out is mechanical and idempotent.
- Missing/incompatible input is reported as `BLOCKED`; a consumer never implements its dependency opportunistically.
- Web is denied by default. The only exception is a yolo 004 executor whose exclusive deliverable is official-documentation research with no implementation; it records direct official URLs and the absolute consultation date. No other role receives web.

## Runtime projections

The local acceptance boundary is materialized files plus parser/schema, complete canonical body, profile, hash, determinism, and collision checks. Builders/tests never execute a coding agent—not even version/help/list/discovery—and never contact a model, provider, auth service, or network.

- **Canonical source:** [[.agents/skills/create-agent-generic/SKILL|create-agent-generic]] maintains `.agents/agents/*.md`.
- **Claude Code:** [[.agents/skills/create-agent-claude-code/SKILL|create-agent-claude-code]] materializes six `.claude/agents/*.md` files. The main session follows `AGENTS.md`; all specialists deny nesting and web.
- **Codex:** [[.agents/skills/create-agent-codex/SKILL|create-agent-codex]] materializes six `.codex/agents/*.toml` files. Planner/Judge use `gpt-5.6-sol` high; the other four use `gpt-5.6-terra` medium.
- **Kimi Code:** [[.agents/skills/create-agent-kimi-code/SKILL|create-agent-kimi-code]] materializes six `.kimi-code/agents/*.md` files. Planner/Judge route `primary`; the other four route `secondary`, fixed by `.kimi-code/config.toml` to `kimi-code/kimi-for-coding` (K2.7) without artificial graduated effort.
- **OpenCode:** [[.agents/skills/create-agent-opencode/SKILL|create-agent-opencode]] materializes six `.opencode/agents/*.md` subagents. Planner/Judge use `kimi-for-coding/k3-256k` high; recon uses `openrouter/qwen/qwen3.5-flash-02-23`; executor uses `openrouter/qwen/qwen3-coder-next`; execution coordinator and phase verifier use `openrouter/deepseek/deepseek-v4-pro` high.
- **Pi:** no adapter. Its current native contract does not provide equivalent custom agents; absence is intentional.

OpenCode splits model identifiers at the first `/`: Kimi subscription IDs use `kimi-for-coding/<model>` and OpenRouter IDs use `openrouter/<organization>/<model>`. There is no central `models.json`; every supported runtime carries its model choice in native agent/config files.

## Invariants

- Planner never executes its plan; judge never performs or dispatches its prescribed repair.
- Every specialist acquires its own context directly from authorized paths; substantive replay by the main session is a violation.
- No specialist expands its own `may_read`, `owns`, permissions, or topology.
- No specialist integrates another branch or moves the kanban; only the main session integrates and transitions.
- An approved front is not rerun or reintegrated because another front returned.
- Parallel work requires satisfied dependencies, logical independence, disjoint writes, and repository/worktree isolation.
- Plans, subtasks, and specs contain decisions and contracts, not chain-of-thought or contingent micro-edits.
- Telemetry persists only stage, contexts, returns, verification strategy/tests, duration, and result.

## Conformance

- [x] Six agent-agnostic specialist sources exist and the main-agent contract lives in `AGENTS.md`.
- [x] Claude Code, Codex, Kimi Code, and OpenCode bundles are materialized locally; Pi and `pop-orchestrator` are absent.
- [x] Runtime model/effort choices are explicit and `models.json` is absent.
- [x] Envelope, direct acquisition, ownership, dependency, gate, and re-entry boundaries survive every projection.
- [x] Builders and validators provide deterministic local evidence without coding-agent or provider execution.
