---
name: delegate-coding
description: Delegates coding work to a headless coding agent CLI (Claude Code, Cursor CLI, opencode or Codex CLI) - invocation contract, tool choice and yolo/auth rules. Use when executing a coding task through another agentic tool instead of doing it directly.
---

# delegate-coding

**Principle: the orchestrator is in control, not the CLI.** The delegated agent runs with full auto-approval; the scope, the isolation and the limits come from the invoker. This hub defines the common contract — each tool's operational detail lives in its own skill.

## Invocation contract (applies to all 4 tools)

1. **Yolo mode always.** The delegated CLI runs with full auto-approval (flags in the table below). Never configure fine-grained permissioning in the CLI — planning and permissions are the orchestrator's responsibility.
2. **Login is a precondition.** The tools are already authenticated on the machine. **An authentication error (mention of credential/login/API key/401/403 in the output, or immediate failure with no work done) completely aborts the orchestrator's task** — no retry, no fallback to another tool, no proceeding with the implementation. Report to the human and stop.
3. **Isolation by the orchestrator:** run the CLI inside a worktree/directory dedicated to the task, never in the main tree.
4. **Scoped prompt:** a single objective, explicit files/areas, a verifiable completion criterion and a "don't touch X" boundary. One task = one session.
5. **Timeout always:** wrap every invocation in `timeout <seconds> <command>` — headless CLIs can hang without exiting.
6. **Parseable output:** ask for JSON format and extract the result, cost and session id; record the id for follow-up.
7. **Verify the result:** the CLI's output is a claim, not proof — check the diff/tests before accepting.

## Tool choice

| If the task needs… | Use | Skill |
|---|---|---|
| Anthropic ecosystem: `.claude/agents/` subagents, CLAUDE.md, JSON Schema output, budget/turn caps | Claude Code | `run-claude-code` |
| Cursor models (composer) or multi-model with a ready-made worktree flag | Cursor CLI | `run-cursor-agent` |
| Multi-provider (`provider/model`), lightweight custom agents in markdown, inline config via env | opencode | `run-opencode` |
| OpenAI ecosystem: ChatGPT plan/GPT-5.x-codex models, native AGENTS.md, JSON Schema-validated response | Codex CLI | `run-codex` |

Tiebreaker: use the **installed** tool (`command -v claude cursor-agent opencode codex`); among installed ones, the one that already has context in the repo (CLAUDE.md → claude; `.cursor/rules/` → cursor; `.opencode/` → opencode; AGENTS.md without CLAUDE.md → codex).

## Yolo flags per tool

| Tool | Yolo | Note |
|---|---|---|
| Claude Code | `--dangerously-skip-permissions` | `-p` alone still asks for permission — the flag is mandatory |
| Cursor CLI | `--force` | without it the agent is read-only; with MCP add `--trust --approve-mcps` |
| opencode | `--auto` | flag of the local installation; the source documents `--dangerously-skip-permissions` — confirm with `--help`; an explicit `deny` in `opencode.json` still wins |
| Codex CLI | `--dangerously-bypass-approvals-and-sandbox` | alias `--yolo`; bypasses approvals **and** the sandbox; no local cost cap — the breaker is the `timeout` |

## Checklist before invoking

- [ ] Tool installed and logged in (auth failure → **total abort**, rule 2)
- [ ] The task's isolated worktree/directory as cwd
- [ ] Prompt with a single objective, completion criterion and boundary
- [ ] The tool's yolo flag + the OS `timeout`
- [ ] JSON format and session id capture
- [ ] Plan to verify the result (diff, tests)

## Skills in this family

- `run-claude-code` — follow it to invoke Claude Code headless.
- `run-cursor-agent` — follow it to invoke the Cursor CLI headless.
- `run-opencode` — follow it to invoke opencode headless.
- `run-codex` — follow it to invoke the Codex CLI headless.
