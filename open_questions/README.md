# open_questions — open questions for the human

Questions and general issues the **agent** has for the human that belong to no kanban card: decisions about new projects, the vault's overall structure, anything that depends on a human decision.

- One file per question: `YYYY-MM-DD-<slug>.md`, from [[_templates/OPEN-QUESTION|OPEN-QUESTION]].
- Frontmatter `status: open | answered` — the open ones show up automatically in the [[INBOX|INBOX]] (Dataview).
- The human answers in the **Answer (user)** section; the agent then applies the answer, marks it `answered` and, if it becomes a harness decision, records it in `notes/decisions/`.

A doubt that belongs to a task uses the card's mechanisms (`(user)` item, `blocked:`, the 003 gate) — this folder is only for what lives **outside** the kanban.
