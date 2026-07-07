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

## Open questions

Questions from the agent that belong to no card — decisions about new projects, overall vault structure etc. (folder `open_questions/`).

```dataview
TABLE WITHOUT ID file.link AS Question, origin AS Origin, created AS "Since"
FROM "open_questions"
WHERE status = "open"
SORT created ASC
```

## In progress now

Informational (no decision needed): tasks with an active agent claim — see the claim rule in [[WORKFLOW|WORKFLOW]].

```dataview
TABLE WITHOUT ID file.link AS Task, project AS Project, claimed_by AS Agent, claimed_at AS Since
WHERE claimed_by
SORT claimed_at ASC
```

## Reviews

Reports from the `weekly-review` skill are linked here, most recent first.

---

Agents: nothing to maintain here beyond the **Reviews** section — the lists above derive from the frontmatter (`stage`, `critical`, `blocked`, `awaiting_merge` on cards; `status` on open questions). To locate gates without Obsidian, run `python3 scripts/pop_status.py` (grep on `stage:`/`awaiting_merge:` works as a fallback).
