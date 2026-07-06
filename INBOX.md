# INBOX

Everything waiting on a decision from you. Lists generated **automatically** by the [Dataview](https://blacksmithgu.github.io/obsidian-dataview/) plugin from the cards' frontmatter — do not edit by hand. Flow: [[WORKFLOW|WORKFLOW]].

## Awaiting plan approval (003)

```dataview
TABLE WITHOUT ID file.link AS Task, project AS Project, updated AS "Since"
WHERE stage = "003_human_approval"
SORT updated ASC
```

## Awaiting verification approval (005, critical tasks)

```dataview
TABLE WITHOUT ID file.link AS Task, project AS Project, updated AS "Since"
WHERE stage = "005_verifying" AND critical = true
SORT updated ASC
```

## Awaiting merge (006)

```dataview
TABLE WITHOUT ID file.link AS Task, project AS Project, pr AS PR
WHERE awaiting_merge = true
SORT updated ASC
```

## Blocked

```dataview
TABLE WITHOUT ID file.link AS Task, project AS Project, blocked_reason AS Reason
WHERE blocked = true
SORT updated ASC
```

## Reviews

Reports from the `weekly-review` skill are linked here, most recent first.

---

Agents: nothing to maintain here beyond the **Reviews** section — the lists above derive from the frontmatter (`stage`, `critical`, `blocked`, `awaiting_merge`). To locate gates without Obsidian: `grep -r "^stage: 003" --include="*.md"`, `grep -r "^awaiting_merge: true"` and equivalents.
