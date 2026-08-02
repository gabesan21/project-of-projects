---
id: coding-dockers
project: pop
domain: harness
kind: contract
status: active
implementation: implemented
origin: "9.1"
created: 2026-08-01
updated: 2026-08-02
supersedes: []
superseded_by:
---

# Spec — Coding dockers

## Contract

Coding dockers provide, only by explicit user choice, a dedicated Linux sandbox for one project × coding agent pair. The agent has its own installation, sees the project at `~/<project>`, and receives no access to the project's parents, neighboring projects, or general host configuration beyond the binds enumerated here.

Operating a coding agent directly at the root of the PoP or another scope remains allowed. No workflow, agent, or command creates or starts a coding docker automatically.

## Expected behavior

- Given a scope and supported agent, when the sandbox is configured, its local artifacts live at `coding-dockers/<scope>/<agent>/`, and only `coding-dockers/INDEX.md` is tracked by Git.
- Given a project without a profile, when the skill inspects first-party manifests at the root or below it, it proposes runtimes, package managers, and tools; ignores dependencies, caches, harness, and symlinks; and writes a versioned local profile only after explicit confirmation of the hash.
- Given a confirmed profile, when `start.sh` is called, the required image and container become available and each call opens a new interactive agent session in `~/<project>`, executing only the canonical TUI binary without flags, prompts, headless mode, or yolo added by the coding docker.
- Given an active container, concurrent `start.sh` calls open independent agent processes sharing only the sandbox, mounted state, and project directory.
- Given an existing container, `stop.sh` stops its processes without removing the image, container, or internal resources.
- Given an existing environment, confirmed `clean.sh` removes the container, image, and internal Docker resources; only host paths declared as profile binds survive.
- Given a project that uses Docker, its client, daemon, images, volumes, networks, and containers belong to the sandbox and do not use the host daemon.

## Invariants

- The supported catalog is exactly `claude-code`, `codex`, `opencode`, `pi`, and `kimi-code`; Cursor and Hermes are not part of this delivery.
- Each sandbox installs exactly one coding agent, its runtime, the project's confirmed stack, and a common base with Git, GitHub CLI, shell, certificates, SSH client, `curl`, `jq`, `ripgrep`, `fd`, `less`, `tmux`, and proper process initialization.
- Node/npm, Yarn, pnpm, PHP/Composer, Python, Go, Rust, Docker, and other project toolchains are installed inside the sandbox only when the confirmed profile requires them; runtime execution never uses host toolchains. Node comes from a pinned and verified official release, currently `22.19.0`.
- The only mounted project content is the target directory at `~/<project>`. Parents, siblings, the PoP root when it is not the target, `/`, `/proc`, `/sys`, and host namespaces are not exposed.
- The sandbox never mounts `/var/run/docker.sock` or another host Docker socket and never runs with `--privileged`; project Docker support conforms only after real proof of its own daemon under this boundary.
- Networking is normal for installing and using agents. Egress proxies, allowlists, and domain blocking are outside the contract.
- Worktrees created in the sandbox stay inside the sole project mount, use relative `gitdir` pointers in both directions, and operate with `gc.auto=0`; no absolute container-only path is recorded as a worktree link.
- The profile explicitly declares the stack, agent recipe, and every persistent bind; no later discovery changes the profile without new user confirmation.

## Interfaces

- **Identity:** input is the absolute project path, scope name, and one of five agent slugs; local output is `coding-dockers/<scope>/<agent>/`.
- **Profile:** local document containing `schema_version`, project, agent, confirmed stack, and persistent binds. Detection produces only a proposal; human confirmation is a precondition for writing.
- **Skill:** `coding-sandbox` operates only when the user explicitly requests a coding docker; it presents a proposal and hash before generating a profile and never integrates with `delegate-coding`.
- **Lifecycle:** `start.sh` ensures an active environment and opens the plain TUI (`claude`, `codex`, `opencode`, `pi`, or `kimi`) without extra arguments; `stop.sh` preserves the environment; `clean.sh` requires confirmation and removes the internal environment.
- **Compatibility:** Arch Linux or Debian-based Linux host; each recipe supplies a reproducible installation of its CLI and runtime inside the image.

### Identity and session binds

The sources below are existing host paths for the user and are mounted directly at the corresponding sandbox-user path:

- Common Git/GitHub: `~/.git-credentials`, `~/.gitconfig`, `~/.config/git`, and `~/.config/gh`.
- Claude Code: `~/.claude`.
- Codex: `~/.codex`.
- opencode: `~/.config/opencode`.
- Pi Agent: `~/.pi`.
- Kimi Code: `~/.kimi-code`.

Each sandbox receives the four common binds and only the selected agent's bind. Copying, exporting, archiving, encrypting, or duplicating this state into a parallel volume is forbidden; CLI changes reflect directly in the local source.

## Errors and limits

- **Missing choice or confirmation:** do not create a profile, image, or container; present the proposal and wait for the user.
- **Missing or incompatible bind source:** abort with the responsible path; do not create a directory in place of a file or fabricate credentials.
- **Agent outside the catalog:** reject the configuration without installing an implicit alternative.
- **Unrepresentable stack:** keep the proposal unwritten and ask for an explicit decision.
- **Own Docker incompatible with the boundary:** do not mount the host socket or relax isolation; support remains nonconforming and returns to the human.
- **`clean.sh` failure:** report remaining internal resources; never delete mounted local paths.
- **Isolation limit:** the sandbox shares the Linux kernel, normal networking, and deliberately mounted files; “isolated” does not promise a virtual machine or protect bind contents from the agent.

## Conformance criteria

The automated suite validates recipes, generation, mounts, isolation, and lifecycle without starting the five coding agents. Authenticated execution of each CLI, including concurrent sessions and Git/`gh` recognition, belongs to the final `(user)` checklist delivered by the Epoch.

- [ ] Creating and starting a sandbox requires explicit action and confirmation, while direct work without a sandbox remains functional.
- [ ] Container inspection finds only the target project and declared identity, session, and persistence binds.
- [ ] All five recipes install and open their agents in the mounted directory without host runtimes; Cursor and Hermes are rejected.
- [ ] Git, `gh`, and the agent recognize the same local session inside the container, without copies or intermediate volumes.
- [ ] A profile is written only after stack proposal confirmation and contains the schema version and complete bind inventory.
- [ ] A project with Docker creates resources only in the internal daemon and works without the host Docker socket or a privileged container.
- [ ] Two `start.sh` calls open independent sessions; `stop.sh` preserves the environment and `clean.sh` removes only internal resources.
- [ ] Worktrees remain valid inside and outside the sandbox through relative pointers, with automatic collection disabled in the container.
- [ ] Networking works without an additional egress policy.
- [ ] The feature exists only in the root PoP and public repository; no file or record is included in a project's installed harness.

## Out of scope

- Automating sandbox choice, replacing direct agent work, or integrating coding dockers with `delegate-coding`.
- Supporting non-Linux hosts, agents outside the catalog, or an egress policy.
- Copying credentials, moving state between machines, or persisting data outside declared local binds.
- Embedding Dockerfiles, scripts, recipes, skill instructions, or runtime artifacts in this specification.

## Related references

- [[coding-dockers/INDEX|Local coding dockers]] — *follow for operation, catalog, lifecycle, and the final user-run acceptance checklist*.
- [[specs/included-standalone|Fully standalone included harness]] — *follow to verify that the feature does not enter the package installed into projects*.
