---
task: <id>-<slug>
project: <category>/<project>
started: YYYY-MM-DD
finished: YYYY-MM-DD
commit: <final (merge) commit hash>
pr: <PR link, if any>
---

# <id>-<slug> — <short title>

Implementation summary in up to **2000 characters**: what changed and where, decisions made, deviations from the plan and pointers (files, specs, PR). Written when closing `006_done`, **after the merge** — it is the task's durable record: the `kanban/006_done/` folder can be cleaned periodically, this file stays and serves as proof of completion for the dependency gate (`depends_on`).
