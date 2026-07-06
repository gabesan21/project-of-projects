# <Project name>

- **Category:** [[agents/INDEX|agents]] | [[applications/INDEX|applications]] | [[writing/INDEX|writing]] | [[work/INDEX|work]]
- **Status:** idea | planning | in progress | paused | completed | abandoned
- **Priority:** high | medium | low
- **Created on:** YYYY-MM-DD
- **Roadmap:** [[<category>/<project>/ROADMAP|Roadmap]]

## Goal

One or two sentences: what does success look like for this project?

## Context

What an agent needs to know before working on this: history, motivation, current state of the world.

## Folder structure

Standard anatomy (see the root AGENTS.md): project `AGENTS.md` + `.agents/skills/`, `ROADMAP.md` + `roadmap/` (epochs), `project/` (per the type — [[TYPES|TYPES]]), `researches/` (researches by topic), `skills/`, `specs/`, `notes/` (learnings/decisions/ideas/references), `memory/` (summaries of completed tasks), `worktrees/` (gitignored), `kanban/` (stages 001–006 of the [[WORKFLOW|WORKFLOW]]). List here only what deviates from the standard.

## Agent harness

Project-specific rules for agents working on this project:

- **Type and repositories:** declared in the [[<category>/<project>/AGENTS|project AGENTS]] (`default` | `included` | `multi-repo`, repos and PR branch — see [[TYPES|TYPES]]).
- **Worktree per task:** yes (default) | no (acceptable only in a project without a git repository — tasks lose isolation and the PR).
- **Tools and restrictions:** what is allowed and what is not.
- **Tone/style:** if applicable.
- **Tasks critical by default?** yes | no — and what makes a task critical in this project (extra human gate in 005, see [[WORKFLOW|WORKFLOW]]).
- **Skills:** list the skills in `skills/` with one line on when to use each.

## Related projects

- [[<category>/<project>/PROJECT|<name>]] — why they relate.

## Decisions

- **YYYY-MM-DD:** decision made and rationale. (If it grows, extract into its own note in `notes/`.)
