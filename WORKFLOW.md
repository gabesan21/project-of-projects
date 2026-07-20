# WORKFLOW — task flow on the kanban

General vault rules: [[AGENTS|AGENTS]] · Inbox: [[INBOX|INBOX]]

Every task is a folder with id `<epoch>.<phase>.<task>-<slug>` that moves as a unit between its project's `kanban/` stages.

## Owner per stage

| Stage | Owner | Runs in | What happens |
|---|---|---|---|
| 001_initial_task | agent (**+ user** releases) | orchestrator | Minimal roadmap card; leaves only after human release. |
| 002_planning | agent | separate planner | Produces a brief: objective, strategy, fronts, contracts, risks and criteria. |
| 003_human_approval | **user** | orchestrator prepares | Human approves the brief; in yolo, the independent reviewer owns the gate. |
| 004_processing | agent | execution orchestrator | Chooses one executor or specialists in sequence/waves and integrates results. |
| 005_verifying | agent (**+ user** if `critical: true`) | independent reviewer | Compares objective, specs, diff, tests and quality; approves or returns. |
| 006_done | agent (**+ user** on merge) | orchestrator | Integration/PR, memory, specs and close-out. |

Every artifact declares its owner. Agents never execute `(user)` items or check `- [ ] Done` for the human. Keep `stage`, `critical`, `blocked` and `awaiting_merge` truthful so INBOX remains correct.

## Orchestration

The main agent controls claim, gates and transitions. Heavy reasoning, operational prompts and specialist coordination are **ephemeral**: the kanban stores decisions, contracts and evidence, not thought transcripts.

Durable contract: [[specs/multi-agent-orchestration|multi-agent orchestration]] — *follow when changing roles, ownership, parallelism or artifacts*.

- **002 — planner always separate:** receives the card and pertinent links and returns `.plan.md`. Delegated recon exists only for a specific question above rule 18's floor; zero workers is normal.
- **004 — adaptive execution:** an execution orchestrator reads the brief and chooses one executor, sequential specialists or parallel waves. The planner never executes.
- **005 — one independent reviewer:** fresh context, distinct from planner and executors; reviews behavior and quality. `critical` raises model/depth, not reviewer count.
- **001 and 006:** remain with the main orchestrator; in yolo, mechanical integration into `develop` is also its job.

Models are selected by role and risk through `scripts/models.json`:

| Role | S | M | L / critical |
|---|---|---|---|
| 002 planner | medium | strong | strong |
| recon worker | — | cheap | cheap |
| 004 execution orchestrator | medium | medium | strong |
| execution specialist | cheap/medium | medium | medium |
| independent reviewer | medium | medium | strong |

`size` estimates effort; it does not authorize automatic ceremony. Uncertainty, risk, skills and front independence determine topology. The Log records only contexts actually launched.

## Contents of the task folder

```
<id>/
├── <id>.md                 ← card
├── <id>.plan.md            ← 002 brief
├── <id>.approval.md        ← 003/006 rounds
├── <id>.verify.md          ← independent 005 review
└── subtasks/               ← persisted fronts only when useful for ownership/gates
    └── <id>.g01-<slug>.md
```

Templates: [[_templates/TASK|TASK]] · [[_templates/TASK-PLAN|TASK-PLAN]] · [[_templates/TASK-APPROVAL|TASK-APPROVAL]] · [[_templates/TASK-VERIFY|TASK-VERIFY]] · [[_templates/SUBTASKS|SUBTASKS]] · [[_templates/MEMORY|MEMORY]].

## Stages

### 001_initial_task — birth (agent, + user releases)

- Create a minimal card: frontmatter, What/Why, phase, dependencies and triggered links.
- The card belongs to the human until `- [x] Ready to plan`. An explicit command lets the agent check it with a Log entry; `yolo: true` inherits roadmap release.
- Declare `depends_on:`. Empty means the task may run concurrently, subject to WIP.
- Suggest `size: S | M | L`; split a task too broad for one cohesive brief.
- Link `[[<id>]]` in the epoch.

### 002_planning — execution brief (agent)

The planner does not implement. It decides and summarizes; it does not persist chain-of-thought, pseudocode, speculative snippets or micro-edits.

- Start with the card and linked research, specs and memory. An open question requiring >~5K tokens of reading may become a recon worker; unresolved gaps become `RECON NEEDED` with the exact check.
- No web: a knowledge gap becomes a prompt in `RESEARCHES.md` + `blocked`; a one-off lookup for an already-decided value is allowed and logged.
- Preflight only when runtime, tooling or services participate; do not repeat irrelevant environment fingerprints.
- Write `.plan.md`: refined objective, strategy, affected areas, fronts, dependencies, specs/skills, material risks/aborts and criteria with run + observable pass.
- Each persisted front describes **delivery and boundary**, never implementation: `owns`, `may_read`, `must_not_edit`, `depends_on`, expected input, skill and criteria. Operational detail belongs in the executor's ephemeral prompt.
- Create/change specs only when the task changes a durable contract; a fix that restores an existing spec only references it.
- Red-team may happen in planner reasoning or through a worker when risk warrants, but its transcript is not mandatory.
- Gate 002→003: verifiable objective; coherent strategy/fronts; explicit dependencies; sufficient contracts; material risks covered; executable criteria; no indispensable decision hidden in reasoning.

### 003_human_approval — human gate (user)

- Add a concise round to `.approval.md`: summary, material risks, main criteria, response and `- [ ] Done`.
- Proceed only with `- [x] Done`: requested changes → 002; approved/empty → 004. In yolo, the independent reviewer performs this sanity check in its own session.
- Enter 004 only when every `depends_on` has `memory/<id>*.md` or a card in the transient 006 window.
- Maximum WIP is three tasks in 004; yolo orchestration prioritizes by dependencies.

### 004_processing — orchestrated execution (agent)

- Create the task integration worktree and `task/<id>` branch in the owning repo; multi-repo projects create one per affected repo.
- The execution orchestrator chooses one executor for one cohesive front/write set, sequential specialists for logical dependencies, or parallel waves for stable contracts with independent write sets.
- Every ephemeral front contract declares `owns`, `may_read`, `must_not_edit`, `depends_on`, `expected_input`, skill, completion criterion and “missing dependency → report BLOCKED; never implement it.”
- Parallel agents use branches/worktrees derived from the task branch. They never integrate peers; the orchestrator centralizes merge/cherry-pick in the integration worktree.
- Before integration, validate the diff with `scripts/pop_check_scope.py --allow ... --deny ...`; return any out-of-scope change, even if correct.
- Do not launch an internal dependency before it is ready. Missing/incompatible input is reported, never created opportunistically.
- Walk applicable DOX before the first edit in each front. Reuse an extract if base/hash has not changed.
- Run the aggregate gate after integration. A `(user)` item, abort, or absent authorized route → `blocked`; a discovery changing objective/contract → 002.
- Record only relevant results, divergences, commits and evidence. Fully integrated and clean → 005.

### 005_verifying — independent review (agent, + user if critical)

- Open fresh context and read in order: objective, specs/contracts, tests and diff. Execution narrative is supporting evidence, not truth.
- Re-run `re-run` criteria; audit `evidence`, promoting it to re-run when inconclusive; run the aggregate gate where applicable.
- Review behavior, edges, tests, complexity, coupling, names, errors, security, docs, specs and touched DOX. For code, follow `clean-code-review`.
- Each finding includes evidence, impact and severity: **blocking**, **suggestion** or **nit**. Only blocking returns to 004/002.
- Exactly one reviewer per round. `critical: true` uses strong/deep review and still waits for the human; in yolo, the same role owns the gate without a second critic.
- Record outcome/evidence by criterion ID without copying the plan. All pass → 006.

### 006_done — integration, merge and close-out (agent + user)

1. Outside yolo, open PR `task/<id>` → declared PR branch, record `pr:`/`awaiting_merge:` and wait. Without a repo, use final approval.
2. In yolo, the orchestrator mechanically synchronizes and integrates `task/<id>` into `develop`; conflict → `blocked`, never autonomous resolution. The reviewer does not operate Git.
3. After merge/integration, write `memory/<id>.md` as a short ledger: result, commit, dates, specs, decisions/divergences and pointers.
4. Synchronize only truly affected specs/DOX; update task/phase/epoch status and indexes if needed.
5. Extract a learning only for reusable knowledge; remove all ephemeral worktrees/branches.
6. Delete `kanban/006_done/<id>/` only after the prior steps; memory is the durable proof.

## Cross-cutting rules

- **An explicit human command beats the flow:** execute, or ask one question if ambiguous/destructive; record the deviation.
- **One run reaches the next human gate:** 001, 003, 005 critical, `(user)`, `blocked` or merge in 006. Collect stage subagents before ending.
- **No work outside a task:** project content changes only in 004 after 003, in the proper worktree.
- **Parallelism requires two independences:** logical and write-set. Specialization may be sequential.
- **Claim is per task:** `pop_claim.py` protects the task folder; front ownership protects workers within it.
- **Transition Log:** one line per move with contexts actually launched; frontmatter stays truthful.
- Moving files use name-only wikilinks. Normal returns: 003→002, 004→002, 005→004.

## Yolo mode

`yolo: true` delegates judgment to the independent reviewer role while retaining the same state machine.

- The human alone sets the roadmap mark. The scope auto-materializes existing tasks, respecting `depends_on` and WIP 3.
- In 003, the reviewer sanity-checks objective, contracts, dependencies, risks and criteria. At most two returns; third → `blocked`.
- In 005, a **new clean session of the same role** reviews implementation and quality; `critical` makes it strong and highlights the task at close-out, without adding an agent.
- Human-owned stops remain: `(user)`, research gap/`blocked`, and final scope review.
- The orchestrator, not the reviewer, integrates tasks into `develop`, with no per-task PR. At scope end it creates an open_question with summary, test instructions and criticals; PR `develop` → PR branch only on human command.
