---
name: charm-lipgloss
description: Terminal styles and layout with the Lip Gloss lib from the Charm ecosystem - declarative styles (colors, borders, padding, alignment), block composition (join/place), table/list/tree subpackages and cell measurement. Use when writing or styling the View of a Go TUI in the vault (Go core, reading TUI, actions TUI), building terminal layouts with side-by-side blocks, rendering static tables/lists/trees or standardizing the visual identity of the PoP TUIs.
---

# charm-lipgloss

**Principle: Lip Gloss is the presentation layer, not the application.** It renders styled strings; the interactive loop is run by Bubble Tea (skill `charm-bubbletea`). All visuals of the vault's Go TUIs go through here — treat styles as design tokens: define them once per package and reuse them.

## What it is / when to use

Lip Gloss is the declarative styling library of the Charm ecosystem (a CSS mental model for the terminal). Use it to style text and assemble the layout of a Bubble Tea program's `View()`, for formatted CLI output without interactivity and for static tables/lists/trees. It is glamour's complement: glamour renders the vault's markdown, lipgloss frames, aligns and colorizes the rest of the screen.

## Installation and imports

```bash
go get charm.land/lipgloss/v2
```

```go
import (
    "charm.land/lipgloss/v2"
    "charm.land/lipgloss/v2/table" // subpackages: table, list, tree
)
```

Use **v2** (`charm.land/lipgloss/v2`) — it is the current version. v1 (`github.com/charmbracelet/lipgloss`) only appears in legacy code; if you find it, follow the official upgrade guide before touching it.

## Core concepts

- **`Style` is an immutable value type:** every method (`Bold`, `Foreground`, `Padding`...) returns a new copy. Assigning (`a := b`) already copies — chain at declaration and reuse the style as a token.
- **Colors:** `lipgloss.Color("205")` (ANSI256) or `lipgloss.Color("#7D56F4")` (hex); named constants for the 16 ANSI colors (`lipgloss.Red`, `lipgloss.BrightCyan`...). Downsampling to the terminal profile is automatic when printing with `lipgloss.Println`/`Sprint`/`Fprint` (drop-in for `fmt`) — with Bubble Tea v2, built in.
- **Block model (CSS):** `Padding`/`Margin` with 1-to-4-value shorthand (clockwise from the top), `Width`/`Height`, `Align(lipgloss.Center)` with `Top/Bottom/Center/Left/Right` positions (0.0 to 1.0), `Border(lipgloss.RoundedBorder(), sides...)` with `BorderForeground`.
- **Ready-made block layout:** `JoinHorizontal`/`JoinVertical` glue aligned multi-line blocks; `Place`/`PlaceHorizontal`/`PlaceVertical` position a block in a blank space.
- **Cell measurement:** `lipgloss.Width`, `lipgloss.Height`, `lipgloss.Size` ignore ANSI sequences and correctly count emoji/CJK — never `len()` on a styled string.
- **Subpackages:** `table` (tables with per-row/column `StyleFunc`), `list` (nested lists with enumerators), `tree` (directory trees).
- **Layers:** `NewLayer`/`NewCompositor` compose overlapping content by coordinate (X/Y/Z) — for most screens, Join + Place are enough.

## Code patterns

Reusable style with border (the "card" pattern of the vault TUIs):

```go
var cardStyle = lipgloss.NewStyle().
    Border(lipgloss.RoundedBorder()).
    BorderForeground(lipgloss.Color("63")).
    Padding(0, 1).
    Width(40)

fmt.Println(cardStyle.Render("Task 1.1.1\nIn planning"))
```

Two-column layout with `JoinHorizontal` and `Place` (list + detail):

```go
list := lipgloss.NewStyle().Width(30).Render("• task A\n• task B")
detail := lipgloss.NewStyle().Width(50).Padding(0, 1).Render(card)

screen := lipgloss.JoinHorizontal(lipgloss.Top, list, detail)
// Center on the whole screen (Bubble Tea: use msg.Width/Height from WindowSizeMsg):
view := lipgloss.Place(width, height, lipgloss.Center, lipgloss.Center, screen)
```

Color adapted to the terminal background (standalone; in Bubble Tea, capture `tea.BackgroundColorMsg`):

```go
hasDarkBG := lipgloss.HasDarkBackground(os.Stdin, os.Stdout)
lightDark := lipgloss.LightDark(hasDarkBG)
title := lipgloss.NewStyle().
    Bold(true).
    Foreground(lightDark(lipgloss.Color("#1a1a1a"), lipgloss.Color("#FAFAFA")))
```

Static table with the `table` subpackage (kanban as text):

```go
t := table.New().
    Border(lipgloss.NormalBorder()).
    BorderStyle(lipgloss.NewStyle().Foreground(lipgloss.Color("99"))).
    Headers("TASK", "STAGE", "OWNER").
    Rows(
        []string{"1.1.1", "004_processing", "agent"},
        []string{"M-2.1", "002_planning", "agent"},
    )

lipgloss.Println(t)
```

## Composition with the other Charm libs

- **bubbletea:** it owns the loop; the `View()` returns a string assembled with lipgloss (Join/Place + styles). Color downsampling is automatic in v2.
- **bubbles:** each component accepts lipgloss styles (e.g. `list.Styles.Title`; in textinput v2, via `SetStyles` with a style per state) — never style the component from the outside with a general `Render`, use its style fields.
- **glamour:** renders the vault's markdown to an ANSI string; frame the output with `lipgloss.NewStyle().Width(...)` or place it in a styled viewport.
- **huh:** themes (`huh.ThemeCharm()` etc.) are built with lipgloss styles.

## Common pitfalls

- **Measuring a styled string with `len()`:** ANSI sequences inflate the size and break the layout — always use `lipgloss.Width`/`Size` to compute alignment and Join.
- **Mixing v1 and v2:** the imports are incompatible (`github.com/charmbracelet/lipgloss` vs `charm.land/lipgloss/v2`); a project uses only one. Current bubbles/glamour are already v2.
- **`fmt.Println` in standalone output:** without the lipgloss writers (`lipgloss.Println`, `Fprint`) there is no downsampling — hex colors leak as raw sequences on terminals without truecolor.
- **Forgetting the frame in the width calculation:** border + padding + margin add to the `Width`; to fit into a space of N cells, subtract `GetHorizontalFrameSize()` (or set `Width` already discounted).
- **Fixed color without checking the background:** a light foreground on a light terminal disappears; use `LightDark`/`HasDarkBackground` (or `tea.BackgroundColorMsg` in Bubble Tea) instead of a single color.
- **`Style` does not mutate:** `s.Bold(true)` alone discards the result — always assign (`s = s.Bold(true)`) or chain.

## Official links

- Repo: <https://github.com/charmbracelet/lipgloss> (README = main documentation, with visual examples)
- v2 API docs: <https://pkg.go.dev/charm.land/lipgloss/v2>
- v1 → v2 upgrade guide: "upgrade guide" link in the repo README
- Charm: <https://charm.land>
