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

> Types explained in [[TYPES|TYPES]]: AI specs can be committed to the repo → `included`; repo must stay clean of harness → `default` (clone in `project/`); one of several repos of the same project → `multi-repo`; several repos that must work standalone, each with a committed harness → `full-multi-repo`.

- **Category** (in `categories/`: `agents` | `applications` | `writing` | `work` — or a new one):
- **Type:**
- **PR branch** for tasks:
- **Kebab-case name** (may differ from the repo name):
- **Project's default language** (the recon confirms it against code and docs):
- **Supported languages (i18n)**, if it is an application:

## Project flow

> What makes the specs faithful — what the code doesn't show.

- **What the project does today**, in your view:
- **Main flows, end to end** (input → processing → output, or the equivalent):
- **What works well** vs. **what is broken/unfinished:**
- **Historical decisions** that explain the current design (they become `notes/decisions/`):
- **How it is delivered/published today:**

## Future (optional)

> Epoch 1 is always "Organization" (specs, skills, research, notes faithful to what exists). Here, what comes after.

- **Destination** — where the project needs to arrive:
- **Candidate post-organization epochs** (one line each):

## Open questions

> What you haven't decided yet and want to discuss with the agent.

-
