<p align="center">
  <img src="assets/pop-logo.svg" alt="PoP — Project Of Projects" width="340">
</p>

<p align="center">
  <b>A second brain for everything you build with AI agents.</b>
</p>

<p align="center">
  <a href="#getting-started">Getting started</a> ·
  <a href="#how-it-works">How it works</a> ·
  <a href="#core-skills">Core skills</a> ·
  <a href="#make-it-yours">Make it yours</a>
</p>

<p align="center">
  <img alt="Obsidian vault" src="https://img.shields.io/badge/Obsidian-vault-f97316">
  <img alt="Agent-agnostic" src="https://img.shields.io/badge/agents-agnostic-f97316">
  <img alt="Human in the loop" src="https://img.shields.io/badge/human-in__the__loop-f97316">
  <a href="LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/badge/license-Apache--2.0-555"></a>
</p>

---

**PoP** is an [Obsidian](https://obsidian.md) vault that catalogs every project in your life — code, writing, work, agents — and gives AI agents the *harness* they need to work on each one: rules, context, specs, skills and a kanban workflow with human approval gates.

This repository does **not** hold your projects' code. It holds their **planning, tracking and agent harness** — and aggregates your real repositories around it.

## Why

Working with AI agents across many projects tends to scatter context everywhere. PoP centralizes it:

- 🗂️ **One vault, all projects** — each with a standard anatomy an agent can navigate blind.
- 🚦 **Humans decide, agents execute** — every task passes a human approval gate before an agent touches real code, and every change ships as a PR that only you merge.
- ♟️ **Plans built like wargames** — recon with parallel subagents, moves with expected observations, forks with triggers, abort conditions, red-teaming. Written so a cheaper executor can run them without asking a single question.
- 🧠 **Durable memory** — every finished task leaves a ≤2000-char memory record, so history survives cleanup.
- 🔌 **Agent-agnostic** — skills live in `.agents/skills/` as plain `SKILL.md` files (the open Agent Skills format). No tool-specific folders; works with Claude Code, Cursor, Codex, opencode and anything that reads `AGENTS.md`.

## How it works

Every project lives in a category folder with the same anatomy — a sheet (`PROJECT.md`), a roadmap (`ROADMAP.md` + `roadmap/`, in epochs → phases → tasks), specs, skills, notes, researches, memory and a kanban every task travels through:

```mermaid
flowchart LR
    A["001<br/>initial task"] --> B["002<br/>planning"]
    B --> C["003<br/>human approval"]
    C --> D["004<br/>processing"]
    D --> E["005<br/>verifying"]
    E --> F["006<br/>done"]
    classDef agent fill:#1f2937,stroke:#4b5563,color:#e5e7eb
    classDef human fill:#f97316,stroke:#c2570c,color:#1c1917,font-weight:bold
    class A,B,D,E agent
    class C,F human
```

<p align="center"><sub>🟧 orange = a human decides &nbsp;·&nbsp; ⬛ dark = an agent executes</sub></p>

- **002 is a wargame:** the agent recons with parallel subagents, then writes a plan a blind executor can follow — route, forks with triggers, abort conditions, acceptance criteria with verification runs, change specs, red-team pass.
- **003 is yours:** nothing touches a repository until you check `- [x] Done`.
- **004 runs in a git worktree** per task (`worktrees/<id>`, branch `task/<id>`), enabling safe parallel tasks.
- **006 opens a PR** — you merge it, the agent writes the memory record and syncs specs.
- **One run = one stage:** an agent invocation executes a single kanban stage and stops. You stay in the loop.

Everything waiting on you shows up in **`INBOX.md`**, generated automatically via Dataview — the one file to open every day.

## Repository structure

```
project-of-projects/
├── AGENTS.md            ← vault rules — the contract every agent reads first (CLAUDE.md → symlink)
├── .agents/skills/      ← the 8 core skills (SKILL.md, agent-agnostic)
├── INDEX.md             ← all projects at a glance + aggregated repositories
├── INBOX.md             ← everything waiting for a human decision (Dataview)
├── WORKFLOW.md          ← the kanban state machine
├── TYPES.md             ← project types: default | included | multi-repo
├── _templates/          ← templates for every standard file
├── agents/              ← AI agents, automations, skills
├── applications/        ← applications and software
├── writing/             ← articles, books, content
└── work/                ← professional projects
```

## Core skills

| Skill | What it does |
|-------|--------------|
| `new-project` | Guided interview that creates a project: essence, harness, roadmap, specs. |
| `import-project` | Imports an existing repository: recon, fit interview, and a mandatory Organization epoch. |
| `plan-roadmap` | Builds/evolves a roadmap by interview (epochs → phases → candidate tasks). |
| `new-task` | Quick interview that materializes a task into the kanban. |
| `advance-task` | Moves a task through the flow 001→006, respecting human gates. |
| `write-spec` | Creates/rewrites a standardized spec. |
| `sync-specs` | Keeps specs faithful to reality as tasks progress. |
| `weekly-review` | Vault-wide review: what waits on you, what stalled, proposals. |

## Getting started

1. **Get the vault** — use this repo as a template (or fork/clone it):
   ```sh
   git clone https://github.com/gabesan21/project-of-projects.git my-vault
   cd my-vault
   ```
2. **Open it in Obsidian** — open the folder as a vault and install the **Dataview** community plugin (powers `INBOX.md`).
3. **Point your agent at it** — open the folder with your AI coding agent. It reads `AGENTS.md` (Claude Code reads it via the `CLAUDE.md` symlink) and learns the whole system from there.
4. **Create your first project** — ask the agent to run the `new-project` skill (or `import-project` for an existing repository) and answer the interview.
5. **Work the loop** — ask for `new-task`, approve plans in `003_human_approval`, ask for `advance-task` to move stages, merge PRs, and check `INBOX.md` daily. Run `weekly-review` once a week.

## Make it yours

- **Language** — the template ships in English; the vault's language is declared in `AGENTS.md` (rule 1) and each project declares its own default language (plus supported i18n languages for applications). Fork it in any language you like.
- **Categories** — `agents`, `applications`, `writing`, `work` are starters. Add your own: create the folder with an `INDEX.md` and register it in `AGENTS.md` and the root `INDEX.md`.
- **Project types** — see `TYPES.md`: keep work inside the vault (`default`), embed the harness in your repo (`included`), or aggregate several repos (`multi-repo`). Clones are always gitignored — the vault stays planning-only.
- **Rules** — the WIP limit, criticality gates and every workflow rule live in `AGENTS.md` and `WORKFLOW.md`. Edit them; the templates in `_templates/` are the single source the skills build from, so keep them in sync.
- **Application context** — programming projects use the **DOX process** (`_templates/DOX.md`): a tree of `AGENTS.md` contract files inside the code, kept honest at every task closeout.

## Credits

- **Developer:** [G. S. Nunes (CariocaWeb3)](https://github.com/gabesan21), using **Fable 5**.
- The application-context model in `_templates/DOX.md` is inspired by the open **DOX** framework (agent0ai/dox, MIT), adapted to be fully self-contained here.
- Skills follow the open **Agent Skills** format (`SKILL.md`), readable by any modern coding agent.

## License

[Apache License 2.0](LICENSE).
