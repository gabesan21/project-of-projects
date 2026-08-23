---
draft: import-project
status: draft
created: YYYY-MM-DD
---

# Import draft — <working name>

> For a project **that already exists** (repository or folder with content). Copy to `drafts/import/<kebab-name>.md` and fill in what you know — these are the questions from the `import-project` skill's interview. The **codebase recon belongs to the agent** (read-only, before creating anything): focus on what the code doesn't show. **"I don't know" is a valid answer.** When done, change `status: draft` → `ready`. The agent confirms the draft against the recon (a divergence becomes RECON NEEDED), files whatever blocks a decision in `open_questions/` and **deletes this file** when materializing. Blockquotes are instructions — delete them when filling it in.

## Location

- **Repository URL** and/or **local path:**

## Fit into the vault

> Types explained in [[TYPES|TYPES]]: AI specs and harness committed to the repo itself → `uni-repo` (the clone in `projects/<project>/` **is** the project, with the entire `pop/` inside it); one of several repos of the same project → `multi-repo` (mother folder in `projects/<project>/` **with no harness** — one clone per repo at the root, each with its own complete `pop/`; no central kanban).

- **Type:**
- **PR branch** for tasks:
- **Kebab-case name** (may differ from the repo name):
- **Project's default language** (the recon confirms it against code and docs):
- **Supported languages (i18n)**, if it is an application:

## Project flow

> What feeds the project's map and notes — what the code doesn't show.

- **What the project does today**, in your view:
- **Main flows, end to end** (input → processing → output, or the equivalent):
- **What works well** vs. **what is broken/unfinished:**
- **Historical decisions** that explain the current design (they become `pop/notes/decisions/`):
- **How it is delivered/published today:**

## Future (optional)

> Epoch 1 is always "Organization" (DOX map, skills, research and notes faithful to what exists — specs only on demand, when work touches the topic). The roadmap is born with it alone; here, what comes after.

- **Destination** — where the project needs to arrive:
- **Candidate post-organization epochs** (one line each):

## Open questions

> What you haven't decided yet and want to discuss with the agent.

-
