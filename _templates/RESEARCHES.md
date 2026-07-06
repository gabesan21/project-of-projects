# Suggested researches — <Project name>

> Blockquotes in this template are fill-in instructions — **delete them when filling it in**.

Profile: [[<category>/<project>/PROJECT|<Project name>]] · Roadmap: [[<category>/<project>/ROADMAP|Roadmap]]

> **Optional** file, next to ROADMAP.md. **Deep research** prompts proposed by the agent for the **user** to run in whatever tool they prefer (deep research) and deposit the result in `researches/<topic>/`. A delivered research enriches the roadmap (epoch recon), the specs and the project itself.

## <topic-in-kebab-case>

- **Status:** pending | delivered → [[<category>/<project>/researches/<topic>/<note>|result]]
- **Feeds:** epoch <n> | spec [[<category>/<project>/specs/<spec>|<spec>]] | RECON NEEDED <which>
- **Suggested prompt:**

> A complete, self-contained prompt: project context in 2–3 sentences, the central question, what the answer needs to cover (comparisons, sources, criteria) and the expected format of the result. It must work pasted into any research tool, without this vault nearby.

## How to use

1. The agent proposes researches here (`new-project`, `plan-roadmap`, `import-project`) — one section per topic.
2. The user runs the prompt wherever they want and saves the result in `researches/<topic>/`.
3. Result delivered → status `delivered` with a link, and the agent reflects the finding in the corresponding roadmap/spec (on the next call).
