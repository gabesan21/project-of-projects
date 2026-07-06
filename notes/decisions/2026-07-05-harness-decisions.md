---
author: agent
created: 2026-07-05
---

# Harness decisions — 2026-07-05

- **PoP as aggregator:** projects may be their own repositories — types in [[TYPES|TYPES]]; clones always gitignored; master list in the root [[INDEX|INDEX]].
- **Human merge and clean 006:** the task worktree becomes a PR in 006 and the merge is always the human's — direct or commanded in the merge round (rule 16 of [[AGENTS|AGENTS]]); `memory/` is the durable record (rule 17), `006_done` may be cleaned and the `depends_on` gate accepts the memory as proof.
- **Strictly agent-agnostic:** skills always as **real copies** in `.agents/skills/` (vault and projects, any type) — no symlinks and no tool-specific folders (`.claude/` etc.); drift between copies is audited by the `weekly-review`.
- **Planning is a wargame:** stage 002 plans for an executor running blind — recon with parallel subagents, Moves with expected observation and counter-move, Forks with trigger, abort conditions, universal red-team (skippable only for a trivial task) and Change specs assembled in the plan (synced in 006, alongside the memory). `.plan.md` up to 200 lines; overflowed → split the task into more boards.
- **Import with Organization gate:** an imported project (`import-project`) receives no change at all until Epoch 1 (Organization) completes — faithful specs, skills, research and notes come first; the gate is declared in the project's AGENTS.md.
- **Single stage per invocation:** the agent never traverses two kanban stages in one run — the stage's work, one transition, stop and report. **Superseded on [[notes/decisions/2026-07-06-harness-decisions|2026-07-06]]** by "one run = up to the next human gate".
- **DOX for applications:** agent context in the code organized by the DOX process, **self-contained** in [[_templates/DOX|_templates/DOX]] (inspired by agent0ai/dox, MIT, no dependency on the repository) — pasted into the project's AGENTS.md, with contracts updated at the close of each task.
