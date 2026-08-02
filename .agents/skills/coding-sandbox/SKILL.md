---
name: coding-sandbox
description: Inspects a project stack and proposes, confirms, and guides an interactive local coding docker for one of five supported agents. Use only when the user explicitly asks for a coding sandbox/docker; never invoke implicitly from a generic Docker mention or for headless delegation.
---

# coding-sandbox

Create one local Linux sandbox per project × agent without exposing neighboring projects. Keep this flow separate from `delegate-coding`: here `start.sh` opens the normal TUI for human use, without flags, prompt, headless mode, or yolo.

## Propose and confirm

1. Confirm that the user explicitly requested the coding sandbox. Without that request, do not inspect, create, start, or alter profiles.
2. Check for Arch Linux or a Debian-based Linux host, Docker, and the five expected bind sources: `~/.git-credentials`, `~/.gitconfig`, `~/.config/git`, `~/.config/gh`, and the selected agent's state. Do not create a missing source or replace a file with a directory.
3. Run only the proposal:

   ```bash
   python3 scripts/pop_sandbox.py new <project> <agent> [--package <package>]
   ```

4. Present the stack, packages, binds, and `confirmation_hash`. Ask for explicit confirmation of that content; do not treat a previous or generic authorization as confirmation of the hash.
5. Stop and wait for the answer. Before it arrives, do not use `--confirm` or write a profile, image, or container.
6. After exact confirmation, repeat the same arguments and add `--confirm <hash>`. If the proposal changed, present the new hash and wait again.

Accepted agents: `claude-code`, `codex`, `opencode`, `pi`, and `kimi-code`. An unrepresentable stack, incompatible bind, or different agent requires stopping for a decision; never accept free-form shell commands or relax isolation.

## Operate

- Check freshness without starting anything: `python3 scripts/pop_sandbox.py --check-fresh <project> <agent>`.
- Open an interactive session: `coding-dockers/<scope>/<agent>/start.sh`. Each call opens another TUI in the same container and project.
- Stop processes while preserving the environment: `coding-dockers/<scope>/<agent>/stop.sh`.
- Remove the container, image, and internal resources: `coding-dockers/<scope>/<agent>/clean.sh`; respect its confirmation. Only then use `python3 scripts/pop_sandbox.py rm <project> <agent>` to delete generated artifacts.
- Never mount a host Docker socket or use `--privileged`. If the project requires Docker, keep its client, daemon, images, volumes, networks, and containers inside the sandbox.

Follow [[coding-dockers/INDEX|Local coding dockers]] for the agent matrix, Git/`gh`, worktrees, and manual `(user)` acceptance. Follow [[specs/coding-dockers|Spec — Coding dockers]] when checking binds, isolation, and contract limits.
