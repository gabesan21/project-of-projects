---
name: run-claude-code
description: Invokes Claude Code as a headless executor of coding tasks (claude -p, yolo mode, sessions, subagents, JSON output). Use when delegating coding work to Claude Code via CLI - general contract and tool choice in the delegate-coding skill.
---

# run-claude-code

Contract, yolo/auth rules and checklist: skill `delegate-coding` — read it before the first delegation. Before the first invocation on the machine, confirm the flags with `claude --help` — versions diverge (the source is from mid-2026; flags below checked against the local installation on 2026-07-12, divergences noted in each section).

## Headless invocation

```bash
timeout 600 claude -p "scoped task" --dangerously-skip-permissions --output-format json
```

- `-p`/`--print`: runs without the TUI and prints the final response. **Alone it does not auto-approve tools** — the yolo flag is mandatory.
- Accepts pipe: `git diff | claude -p "review this diff" ...`.
- `--bare` skips MCP, CLAUDE.md and hooks (~10x faster) — use for one-off tasks that don't need the repo's context.

## Output and parsing

- `--output-format text|json|stream-json`. The JSON carries `result`, `session_id`, `total_cost_usd`, `usage{input_tokens, output_tokens, ...}`.
- `--json-schema '<schema>'` forces the response into a JSON shape — use it when the orchestrator will parse fields.
- `stream-json` is NDJSON (one event per line) for tracking progress.

```bash
claude -p "..." --dangerously-skip-permissions --output-format json | jq -r '.result, .session_id, .total_cost_usd'
```

## Sessions

- Create a named one: `claude -n "task-name" -p "..."` (or `--session-id` to pin the id).
- Continue the directory's most recent: `claude --continue -p "..."`.
- Resume a specific one: `claude --resume <id|name> -p "..."`.
- Alternative without touching the original: `--fork-session`.
- Record the `session_id` from the JSON; a follow-up of the same task reuses the session, a new task creates another.

## Yolo mode

`--dangerously-skip-permissions` — auto-approves everything. It is this skill family's default mode (decision of 2026-07-12): control comes from the orchestrator (isolated worktree, scoped prompt, timeout), not from permission flags. Fine-grained permissioning (`--allowedTools`, `--permission-mode` etc.) exists, but is **not used** here.

## Specific agents

- Built-in subagents: `Explore` (read-only), `Plan` (read-only), `general-purpose` — invoked automatically; influence them via prompt ("use the Explore subagent to...").
- Custom: markdown file in `.claude/agents/<name>.md` (project) or `~/.claude/agents/` with frontmatter `name`, `description`, `tools`, `model`, `skills`.
- System prompt: `--append-system-prompt "text"` or `--append-system-prompt-file <path>`; `--system-prompt-file` **replaces** the entire system prompt.
- `claude agents` lists the configured ones.

## Model

`--model <model>` — confirmed on the local installation (the source did not document it). Persistent alternatives: `settings.json` (`"model": "..."`) or per subagent (`model` frontmatter).

## MCP

Servers in `settings.json` under `mcpServers`; `claude mcp list` checks. MCP adds startup latency — `--bare` skips it all when not needed.

## Context and directories

- Run with the cwd already inside the task's worktree (the source's `--directory` **does not exist** on the local installation); `--add-dir <path>` (repeatable) grants access to extra directories.
- `-w/--worktree <name>` creates an isolated git worktree in `.claude/worktrees/<name>` — an alternative when the orchestrator hasn't isolated yet.
- The repo's `CLAUDE.md` loads automatically, but it is advisory (not guaranteed).

## Auth

Precondition: already logged in (or `ANTHROPIC_API_KEY` in the environment). **Do not configure login in this skill.** If the output mentions credential/API key/login/401: **abort the orchestrator's entire task** — no retry, no fallback; an immediate failure with **no** auth signal is an invocation error, not a login one (rule 2 of `delegate-coding`).

## Gotchas

- `AskUserQuestion` hangs/fails in headless — the prompt must give all the information and forbid questions.
- Add its own circuit breakers: `--max-budget-usd <value>`, on top of the OS `timeout` (the source's `--max-turns` **does not exist** on the local installation).
- CLAUDE.md is advisory: a critical instruction goes in the prompt, not only in the file.

## Recipes

```bash
# Audit with structured output
timeout 600 claude -p "Audit src/auth/ and list vulnerabilities" \
  --dangerously-skip-permissions --output-format json --json-schema '{"type":"object","properties":{"issues":{"type":"array"}}}'

# Editing task in its own worktree, with a cost breaker
timeout 900 claude -w task-fix-login -p "Fix bug X in src/login.ts; run the tests; don't touch other files" \
  --dangerously-skip-permissions --output-format json --max-budget-usd 2

# Quick, without the repo's context
timeout 300 claude --bare -p "Explain the diff on stdin" --dangerously-skip-permissions < diff.txt

# Named session + follow-up
claude -n "refactor-auth" -p "..." --dangerously-skip-permissions --output-format json
claude --resume "refactor-auth" -p "now run the tests" --dangerously-skip-permissions --output-format json
```

## See also

- Contract and choice: `delegate-coding` · Same operation in another tool: `run-cursor-agent`, `run-opencode`, `run-codex`.
