---
name: ui-review
description: UI review with evidence - Nielsen heuristics as pass/fail with severity 1-4, two-layer WCAG 2.2 AA and a screenshot→vision visual verification loop iterating until severity <2. Use when verifying or reviewing UI in frontend tasks (005) and in plan or PR gates. Frontend projects only.
---

# ui-review

**Principle: a UI review produces evidence — a screenshot, a measurement, a violated criterion — not a vibe check.** "Looks good" is not a verdict; "the primary button is 32px tall, below the 44px minimum" is. Whoever writes the UI uses the sibling skill `ui-change`; this one reviews against its contract (`DESIGN.md`, tokens, states).

**Parametrization:** run the commands declared in the **"Project verification"** section of the project's AGENTS.md (Playwright, axe-core, Lighthouse, token lint). This skill describes the verification loop — it **never installs a tool**.

## Reading script

1. Read the **contract** first: `DESIGN.md`, tokens and the component inventory; only then the change, in the order the user experiences it.
2. Verify in this order: automated layer (2a) → heuristics (1) → semantics (2b) → visual loop (3) → decision.

## 1. Nielsen heuristics as pass/fail

**Trigger:** every UI review — the quick version of the process; the full audit of the 10 heuristics is `nielsen-heuristics-audit`.

Each heuristic becomes a question with a verification method, for example: does every action have visual feedback in <200ms (before/after screenshot)? Is there back/undo at every step? Are identical components identical (compare with the inventory)? Inline validation before submit? Is there more than 1 primary button in the same context? Does the error message explain the problem and suggest an action?

**Severity of each finding (1-4 scale):** 1 cosmetic (doesn't prevent the task) · 2 minor (a workaround exists) · 3 major (prevents the task) · 4 catastrophic (makes use impossible).

**Verifiable output:** a pass/fail list with severity and evidence (screen, element, measurement) per finding.

## 2. Two-layer WCAG 2.2 AA

**Trigger:** every review; the full POUR audit is `wcag-accessibility-audit`.

- **(a) Automatable (~30% of the problems, fails the build):** the project's axe-core/Lighthouse — alt text, contrast ≥4.5:1 (≥3:1 non-text), visible focus, targets ≥24×24px, associated labels, ARIA on custom components. A violation here is always blocking.
- **(b) Semantic (~70%, reviewer prompts):** does the tab order follow the visual layout? Does focus get obscured by a sticky header/modal? Are loading/success/error announced via aria-live? Does any field repeat information already provided? Does 200% zoom break the layout?

**Verifiable output:** a report citing the WCAG criterion per failure + the proposed fix.

## 3. Visual verification loop

**Trigger:** a visual change implemented — the loop runs **before** handing back to the human.

1. Headless screenshot (the project's tool, e.g. Playwright) at the **3 viewports: 375, 768 and 1440px**.
2. Examine each screenshot with your own vision: overlapping elements, missing content, incorrect alignment, confusing hierarchy — compare with the `DESIGN.md` and the approved baseline.
3. List each problem with severity 1-4 and a specific fix; apply; new screenshot.
4. Iterate **until no problem of severity ≥2 remains** — a specific diff per item, never "looks good".

**Verifiable output:** final screenshots of the 3 viewports + a record of the iterations and what changed in each one.

## Known limits (declare them in the report)

- **Pixel diff yields 15-30% false positives** (anti-aliasing, fonts, browser) — prefer semantic critique via vision over pixel diff; if you use diff, pin the browser and fonts.
- **Vision fails on text <12px** in a 1x screenshot — increase the zoom/scale to check microtext and don't pass legibility without it.
- Real coverage per dimension: contrast 95%+, ARIA semantics ~70%, **visual hierarchy ~30%**, legibility ~20% — final aesthetic judgment remains human; don't report the loop as a total guarantee.

## Decision

| Severity | When | Effect |
|----------|------|--------|
| **blocking** | Finding of severity ≥3, automatable WCAG violation, missing mandatory state, raw hex outside tokens | Prevents approval until resolved |
| **suggestion** | Severity 2 with a workaround, justified hierarchy/consistency improvement | Author decides; record the reason |
| **nit** | Severity 1, aesthetic preference | Never holds the change |

- **Approve** when the change improves visual and accessibility health, even if imperfect; deferral becomes a trackable follow-up.
- **Send back** (in the PoP: 005 → 004/002) only over a blocking item, citing the heuristic/criterion and the evidence.

## Supporting vendored skills

Reference them by **folder name** in `.agents/skills/` — read, don't copy:

- `nielsen-heuristics-audit` — full audit of the 10 heuristics, when section 1 is not enough.
- `wcag-accessibility-audit` — WCAG 2.1/2.2 audit through the POUR principles, for deep a11y.
- `skill-a11y-audit` — accessibility audit with its own scripts, when the project allows running them.
- `ui-design-review` — in-depth visual/aesthetic evaluation (typography, color, spacing, hierarchy).
- `web-design-guidelines` — checking the UI code against the Web Interface Guidelines.
- `cognitive-walkthrough` — simulating a novice user's cognition on a specific critical task.
- `don-norman-principles-audit` — dedicated audit through Don Norman's 7 principles.
- `ux-audit-rethink` — holistic UX audit with redesign proposals, when the problem is structural.

## What this review is not

- It does not verify motion/timing, real touch on device, cultural/RTL context or perceptual performance (jank) — declared gaps of the research.
- `npx ai-visual-review` is pseudocode from the research, with no source — it is neither a dependency nor a runnable example.
- It does not install tools and does not audit the whole repository: the scope is the change and what it touches.
- It does not duplicate the vendored skills — it points to them by folder name, with a trigger.
