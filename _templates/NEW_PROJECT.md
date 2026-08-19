---
draft: new-project
status: draft
created: YYYY-MM-DD
---

# New project draft — <working name>

> Copy this file to `drafts/new/<kebab-name>.md` and fill in what you know — these are the same questions as the `new-project` skill's interview. **"I don't know yet" is a valid answer**: leave it blank or write the doubt. When done, change `status: draft` → `ready`. When engaged, the agent uses the draft as a pre-answered interview (it confirms, it doesn't re-ask), files whatever blocks a decision in `open_questions/` and **deletes this file** when the project is materialized. Blockquotes are instructions — delete them when filling it in.

## Essence

- **What the project is** (1–2 sentences):
- **Success** — how you'll know it worked:
- **Kind** (programming, writing, business, research, personal...):
- **Kebab-case name** (proposal — becomes the folder in `projects/<name>/`, with no category level):

## Type and repositories

> Types explained in [[TYPES|TYPES]]: `uni-repo` (the folder in `projects/<project>/` **is the repository itself**, with the entire `pop/` committed into it — or a free root with no repo, versioned in the PoP) | `multi-repo` (mother folder in `projects/<project>/` **with no harness** — one clone per repo at the root, each with its own complete `pop/`; no central kanban — tasks live in the repos).

- **Type:**
- **Repository(ies)** — URL and name of each: optional (one) if `uni-repo`; **all of them**, if `multi-repo`:
- **PR branch** — where task worktrees open PRs to (e.g. `main`):

## Context and harness

- **Tools and constraints** agents must respect:
- **Tone/style**, if applicable:
- **Tasks critical by default?** (extra human gate on verification — yes/no):
- **Related projects in the vault:**
- **Project's default language** (specs, notes, research, code comments):
- **Supported languages (i18n)**, if it is an application:

## Roadmap (optional)

> The `plan-roadmap` skill refines this with you — a sketch is enough here.

- **Destination** — where the project needs to arrive:
- **Candidate epochs** (one line each):
- **Topics that call for deep research** (become prompts in RESEARCHES.md):

## Initial specs (optional)

- **Topics that deserve a spec right away** (one line each):

## Open questions

> What you haven't decided yet and want to discuss with the agent.

-
