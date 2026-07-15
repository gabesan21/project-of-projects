---
name: ui-change
description: UI design and implementation process - a single decisive tone, design tokens as a lintable contract, DESIGN.md as persistent memory, mandatory states per component and an anti-drift inventory. Use when designing or implementing UI (screens, components, styles), when planning (002) and when executing (004). Frontend projects only.
---

# ui-change

**Principle: good UI is born from an executable visual contract, not from the agent's taste.** Agents are blind to the render, have no design memory and converge to the statistical average (Inter, purple gradient, three cards). The antidote is not "prompting better": it is architecting the context — a decided tone, tokens as a contract, a persistent `DESIGN.md`. This skill accompanies whoever **writes** UI; verification uses the sibling `ui-review`.

**Parametrization:** lint, framework, build and screenshot tools are the ones declared in the **"Project verification"** section of the project's AGENTS.md. This skill describes the process — it **never installs a tool**.

## 1. Tone: one decisive aesthetic direction

**Trigger:** a new project or screen with no visual direction declared in the `DESIGN.md`.

1. Choose **ONE** nameable direction (editorial, brutalist, industrial, art déco...) — never "modern and clean".
2. Collect real visual reference and **extract the language** into reusable rules (a typographic scale with 3x+ jumps, spacing rhythm, dominant color + accent on <10% of the area) — don't copy pixels.
3. Record in the `DESIGN.md` the direction, the reference and the **banned fonts** (the generic default to avoid).

**Verifiable output:** the `DESIGN.md`'s Tone section with a single named direction and the extracted reference.

## 2. Design tokens as a contract

**Trigger:** any visual value (color, spacing, radius, shadow, type) about to enter the code.

1. Every value enters through a **semantic name**, never raw: `color.feedback.error`, not `#DC2626` — the name carries the intention.
2. Minimum structure: `color` (text/surface/action/feedback), `spacing` (scale), `radius`, `shadow`, `type` (scale/weight/lineHeight).
3. Make the contract **executable by lint**: a rule that rejects literal hex (`#RRGGBB`) and raw values outside `tokens/` — the command is the one in the project's AGENTS.md.
4. Theme (dark mode, brand variant) changes tokens, never components.

**Verifiable output:** tokens defined + the anti-hex lint passing with 0 raw values outside `tokens/`.

## 3. DESIGN.md as persistent memory

**Trigger:** the start of any UI session — a missing or outdated `DESIGN.md` blocks everything else.

1. The `DESIGN.md` at the frontend's root is the contract that survives between sessions: tone, typography, colors by token, spacing rhythm, states and composition rules.
2. Every component declares the **6 mandatory states**: default, loading (skeleton/spinner), empty (message + CTA), error (descriptive message + retry), hover/focus (visible, outline ≥2px) and disabled (visually distinct).
3. Composition rules are numeric and verifiable: **max. 1 primary button per section**, label above the input, text max-width 65ch.
4. A new visual decision made in the task → updates the `DESIGN.md` in the same task.

**Verifiable output:** a `DESIGN.md` that exists and is faithful to the code at the end of the change.

## 4. Anti-drift component inventory

**Trigger:** **before** creating any new component.

1. Inventory the existing primitives (buttons, inputs, cards, modals, tables) with their import path and main props.
2. Build the screen using **only** those components wherever they exist; flag what is genuinely new.
3. Never create a second button style — component drift is a bug, not a variation.

**Verifiable output:** the inventory listed in the task + a 1-line justification for every component created.

## 5. Screen-by-screen implementation with numeric laws

**Trigger:** when coding each screen, one at a time, against the contract of sections 1-4.

1. UX laws with a number, not a vibe: action targets **≥44×44px** (Fitts); a menu with **>7 items** requires grouping or search (Hick); related items at **≤16px**, unrelated at **≥32px** (proximity); groups of up to 7±2 items (Miller); multi-step forms with a progress indicator.
2. The 6 states from the `DESIGN.md` implemented and visually distinct in every component of the screen.
3. **WCAG 2.2 AA is a design entry gate**, not a final step: contrast ≥4.5:1, visible focus, associated labels and keyboard navigation come in together with the layout — the two-layer verification belongs to `ui-review`.

**Verifiable output:** a screen with complete states and the laws met, ready for `ui-review`'s visual loop.

## Supporting vendored skills

Reference them by **folder name** in `.agents/skills/` — read, don't copy:

- `frontend-design` — distinctive visual direction and escaping the generic default, when defining the tone.
- `taste-skill` — inferring the design direction from the brief, for landing pages, portfolios or redesigns.
- `impeccable` — designing, critiquing and polishing interfaces with anti-pattern detectors, during implementation.
- `design-tokens` — validating and structuring tokens in the DTCG spec, when building section 2's contract.
- `color-expert` — palettes, contrast and color perception, when choosing the tokens' values.
- `shadcn` — adding and composing shadcn/ui components, when the project uses them.
- `react-best-practices` — React/Next.js performance, when implementing in React projects.
- `web-design-guidelines` — checking the UI code against guidelines, when closing each screen.

## What this skill is not

- It does not cover motion/timing, real touch on device, cultural/RTL context or perceptual performance — declared gaps of the research, outside the current verifiable reach.
- It does not install Playwright, axe-core or lint — tools are parametrized in the project's AGENTS.md.
- It is not the review: Nielsen, two-layer WCAG and the screenshot→vision loop belong to the sibling `ui-review`.
- It does not replace the vendored skills — it references them by folder name, never duplicates their content.
