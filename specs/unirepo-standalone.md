---
id: unirepo-standalone
project: pop
domain: harness
kind: contract
status: active
implementation: implemented
origin: "11.2"
created: 2026-08-18
updated: 2026-08-18
supersedes: [included-standalone]
superseded_by:
---

# Spec — Fully standalone uni-repo harness

## Contract

Defines the verifiable contract of a `uni-repo` project's repository: once cloned in isolation and opened as the `cwd`, it provides the complete PoP harness without reading files from the host that installed it.

## Expected behavior

- An isolated clone runs stages 001→`005_closing`, including normal and yolo tasks, using only files versioned in the repository itself and declared external tools.
- `AGENTS.md` and the `CLAUDE.md` symlink make the root instructions discoverable; agents without native discovery of `.agents/skills/` get an explicit local instruction to read the skills.
- Every skill referenced by instructions, cards, installed skills or the workflow exists locally; the transitive closure mandatorily includes the yolo-critical ones.
- The six canonical sources in `.agents/agents/`, the five supported `create-agent-*` skills and the native projections for Claude Code, Codex, Kimi Code and OpenCode are managed files at the repository root; Pi, `pop-orchestrator` and any `models.json` remain absent.
- Local configurations outside the managed inventory, such as `.claude/settings.local.json` and OpenCode dependencies/cache, survive installation and update.
- `pop/scripts/validate_local_agents.py`, run without `--root`, detects the anatomy through the `pop/.unirepo-harness.json` marker and validates the bundles at the repository root without invoking a coding agent, provider or network.
- Every internal script or command referenced by the workflow and the skills exists locally, resolves imports from the repository root and offers a documented fallback only when functionally equivalent.
- `INBOX.md`, `open_questions/`, templates and the kanban structure required by the human gates and yolo close-out exist in the isolated clone.
- Every internal wikilink of the project resolves inside the repository itself: the installer strips the `projects/<project>/` prefix when materializing the package, and the installed content never names the host — `--audit-boundary` rejects tokens such as `projects/`, "meta-project" and "root/parent PoP" in the text that reaches the target.
- Specs, roadmap, research, notes, memory and DOX contracts use local links with a trigger whenever the context protocol requires one.
- The local validation command succeeds on an isolated clone and detects any missing required skill, script, link or file.
- The declarative manifest (`_templates/unirepo-manifest.json`) is the single list of the package; the installer (`scripts/pop_install_unirepo.py`) and the validator consume it, and `new-project`/`import-project` only call the installer without repeating inventories.
- Installation and update use the same idempotent command: they change only package-managed paths, preserve the project's content and abort on an unsafe collision.
- The update **mirrors**: a file removed from the source is removed from the target based on the previous install's inventory, so the clone does not keep offering a template or script the flow has retired. The package propagates neither the host's test suite nor its bytecode.
- Every install stamps into `pop/.unirepo-harness.json` the managed set's `content_sha` at the origin plus the inventory of what it wrote; `--check-fresh` recomputes it and **fails closed** when the target fell behind. Without the stamp, a clone parked on an old version of the flow is indistinguishable from a current one.
- The host's validator treats a stale or unstamped target as a violation, with the fix command in the message.
- The installed scope labels itself by the name of its own root; validation that compares the scope label (`project:` in memory and specs) demands equality only where sibling projects exist — in the standalone clone the field need only be filled.
- Installed templates generate local links; validation rejects host paths both in the package and in artifacts filled in from them.
- Each repo of a `multi-repo` project receives exactly the same standalone contract, plus the local membership links (the "Part of" section) that don't break its isolated use.
- A temporary fixture materialized by both flows proves the package works without the host on the filesystem.
- Existing `uni-repo` projects have a deterministic update procedure: rerun the install command.

## Invariants

- Markdown, frontmatter and Git remain the installed harness's source of truth.
- The declarative manifest is the single list of the package; the installer and the validator consume it.
- The only recognized marker is `pop/.unirepo-harness.json`, with no legacy-layout fallback; `poplib.vault_root()` stops at it — an installed harness is a complete world.
- Installation changes only managed paths and never depends on the host's filesystem.

## Interfaces

- **Input:** the package manifest and the root of a `uni-repo` repository.
- **Output:** a complete, validatable standalone harness at the project root, stamped in `pop/.unirepo-harness.json`.
- **Compatibility:** a `uni-repo` clone and each repo of a `multi-repo` receive the same local contract.

## Errors and limits

- **Missing dependency or link external to the project:** validation fails with the responsible path.
- **Unsafe collision on a managed path:** installation aborts without overwriting the project's content.
- **Package that names the host:** the install is rejected by the boundary gate before writing.
- **Limit:** standalone eliminates runtime dependencies on the host, not the provenance of the installed copies.

## Conformance criteria

- [x] An isolated clone runs 001→`005_closing`, including the yolo flow, with only local files and declared tools.
- [x] The transitive closure of skills, scripts, templates and required files is validated.
- [x] Temporary fixtures materialized by the supported flows pass without the host on the filesystem.
- [x] The marker, the manifest and the installer follow the uni-repo vocabulary, and the boundary audits the post-localize text under the `projects/<project>/` model.

## Out of scope

- Changing the functional code of the projects that receive the harness.
- Giving the parent folder of a `multi-repo` a harness: by sovereign decision it has none — the contract applies per repo.
- Creating tool-specific skill sources; `.agents/skills/` remains the agent-agnostic source.

## Open questions

- No open architecture point; a divergence found during execution goes back to 002 instead of silently expanding the package.

## Related references

- [[TYPES|TYPES]] — *follow for the current type model (`uni-repo`/`multi-repo`) and the location of the repositories*.
