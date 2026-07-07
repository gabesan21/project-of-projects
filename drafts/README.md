# drafts — project drafts

Drafts filled in by the **human** to sketch several projects before engaging an agent:

- `new/` — new projects, from [[_templates/NEW_PROJECT|NEW_PROJECT]].
- `import/` — projects/repositories that already exist, from [[_templates/IMPORT_PROJECT|IMPORT_PROJECT]].

**Flow:** copy the template, fill in what you know ("I don't know" is a valid answer), change `status:` to `ready`. When engaged, the agent follows the corresponding skill (`new-project` / `import-project`) using the draft as a pre-answered interview: it confirms instead of re-asking, files questions that block a decision in `open_questions/` and **deletes the draft** when the project is materialized — its content then lives in the project's folder.

The `weekly-review` lists stalled `ready` drafts in its **Proposals** section.
