# Plan defense — [[<id>-<slug>]]

> Blockquotes are filling instructions — **delete them when filling**.

- **Stage:** 002_planning · **Owner:** planner agent

> **Adversarial-gate artifact.** It is born together with the plan when the task is `yolo: true` **and** (`size: L` **or** `critical: true`) — without it the devil's advocate has nothing to attack and act 1 returns the task to 002. No other configuration produces this file.
> **Ceiling: 30 lines** (validated by `pop_validate`). Not fitting means the plan concentrates too much decision for a single task — not that the defense should compress.
> This is a **short list of contestable decisions**, never chain-of-thought, pseudocode or a transcript of reasoning: record the decision and what would knock it down, not the path to it.
> A decision with no real alternative and no falsifier is not a decision, it is filler — and it becomes noise for whoever attacks. Order by consequence: the choice that is most expensive to reverse comes first.

## Contestable decisions

| # | Decision | Choice adopted | Alternative rejected | Why | What would falsify it |
|---|----------|----------------|----------------------|-----|-----------------------|
| 1 | <the point in dispute> | <what the plan does> | <the discarded option> | <reason, one line> | <the observation or run that would prove the choice wrong> |
