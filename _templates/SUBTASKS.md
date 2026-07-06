# Group <g01> — <group name> — [[<id>-<slug>]]

- **Order:** this group's position in the execution (see [[<id>-<slug>.plan|plan]]).
- **Depends on:** prerequisite groups (e.g. `g01`) — empty = can run in parallel with the other groups.
- **Description:** one line — what this group delivers together.

## Moves

> Every item declares its owner: `(agent)` or `(user)`. Agents never execute a `(user)` item — they signal and wait.
> An item that requires another item completed first notes `(after <ref>)`; without the note, items in the group can be parallelized.
> Every `(agent)` move carries **Expect to see** (the observation that confirms it worked) and **If it fails** (likely failure → cause it signals → counter-move).

- [ ] (agent) Objective, executable and verifiable move.
  - Expect to see: <exactly what should be observed if it worked>.
  - If it fails: <likely failure> → <cause it signals> → <counter-move>.
- [ ] (agent) (after previous) Move that needs the first one completed.
  - Expect to see: <observation>.
  - If it fails: <failure> → <cause> → <counter-move>.
- [ ] (user) Action only the human can do (e.g. create an account, approve a purchase) — say what they should hand back.

## Execution notes

- YYYY-MM-DD — findings, deviations from the plan, links to what was produced.
