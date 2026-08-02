# Local coding dockers

This directory receives local Linux sandboxes per project × agent, created only by explicit request and proposal confirmation. Only this index is versioned; profiles, rendered scripts, images, and runtime state remain local.

- [[.agents/skills/coding-sandbox/SKILL|coding-sandbox skill]] — *follow when the user explicitly asks to propose or operate a sandbox*.
- [[specs/coding-dockers|Spec — Coding dockers]] — *follow to check isolation, binds, and promised limits*.

Do not use this flow for headless delegation: `delegate-coding` has a different contract. Each `start.sh` opens only the canonical TUI, without flags, prompts, headless mode, or yolo.

## Prerequisites and proposal

- Arch Linux or Debian-based Linux host, working Docker Engine, and the `bash`, `jq`, and GNU coreutils tools.
- A project recognized by the harness and existing bind sources of the correct type; the generator never fabricates credentials.
- Run `python3 scripts/pop_sandbox.py new <project> <agent>` only to inspect. Check the stack, packages, five binds, and `confirmation_hash`; no profile is written at this stage.
- Only after the user confirms the exact proposal, repeat the same arguments with `--confirm <confirmation_hash>`. A changed proposal or hash requires a new confirmation.

## Authenticated catalog

Every sandbox receives four common RW binds: `~/.git-credentials`, `~/.gitconfig`, `~/.config/git`, and `~/.config/gh`. It also receives exactly one RW agent bind:

| Agent | Reproducible image installation | Session bind | Plain `start.sh` TUI |
|-------|---------------------------------|--------------|----------------------|
| Claude Code (`claude-code`) | `npm install --global @anthropic-ai/claude-code` | `~/.claude` | `claude` |
| Codex (`codex`) | `npm install --global @openai/codex` | `~/.codex` | `codex` |
| opencode (`opencode`) | `npm install --global opencode-ai` | `~/.config/opencode` | `opencode` |
| Pi Agent (`pi`) | `npm install -g --ignore-scripts @earendil-works/pi-coding-agent` | `~/.pi` | `pi` |
| Kimi Code (`kimi-code`) | `npm install -g @moonshot-ai/kimi-code` | `~/.kimi-code` | `kimi` |

State is mounted directly at the matching path under `/home/coder`; it is not copied, exported, or duplicated into an intermediate volume.

## Lifecycle and sessions

1. `coding-dockers/<scope>/<agent>/start.sh` creates the image/container when needed and opens the TUI in `/home/coder/<project>`.
2. Concurrent `start.sh` calls open independent processes that share only the container, project, and declared binds.
3. `coding-dockers/<scope>/<agent>/stop.sh` stops the container while preserving the image and internal resources; another `start.sh` resumes the environment.
4. `coding-dockers/<scope>/<agent>/clean.sh` asks for confirmation and removes the container, image, and internal Docker resources while preserving every bind source.
5. After `clean.sh`, `python3 scripts/pop_sandbox.py rm <project> <agent>` removes only the generated local artifacts.

When the stack includes Docker, the daemon, socket, images, volumes, networks, and containers belong to the sandbox. Never mount `/var/run/docker.sock` or another host socket, use `--privileged`, or resort to an `unconfined` profile.

## Git, GitHub CLI, and worktrees

Inside the container, run `git status --short` and `gh auth status` as `coder`, with `HOME=/home/coder` and the project as workdir, to verify the same repository and local session. Do not print tokens or copy configuration.

Create worktrees only inside the project mount, for example `git worktree add --relative-paths .worktrees/<name> -b <branch>`. Check that `gitdir` pointers are relative in both the worktree and main repository and that `gc.auto=0` applies in the container; remove the proof afterward. The worktree must remain valid inside and outside the sandbox.

## Final authenticated acceptance `(user)`

This checklist is manual and remains unchecked until the user runs every recipe. Automation and the Epoch do not start or query agent binaries.

- [ ] `(user)` Claude Code installs and opens `claude` without arguments; recognizes its session, Git/`gh`, two simultaneous TUIs, a relative worktree, restart, and safe `clean`.
- [ ] `(user)` Codex installs and opens `codex` without arguments; recognizes its session, Git/`gh`, two simultaneous TUIs, a relative worktree, restart, and safe `clean`.
- [ ] `(user)` opencode installs and opens `opencode` without arguments; recognizes its session, Git/`gh`, two simultaneous TUIs, a relative worktree, restart, and safe `clean`.
- [ ] `(user)` Pi Agent installs and opens `pi` without arguments; recognizes its session, Git/`gh`, two simultaneous TUIs, a relative worktree, restart, and safe `clean`.
- [ ] `(user)` Kimi Code installs and opens `kimi` without arguments; recognizes its session, Git/`gh`, two simultaneous TUIs, a relative worktree, restart, and safe `clean`.
- [ ] `(user)` In a project with Docker, resources appear only in the internal daemon, without the host socket or `--privileged`, and `clean` removes internal resources while preserving binds.
