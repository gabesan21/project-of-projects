---
name: charm-glamour
description: Renders styled markdown in the terminal with the glamour library from the Charm ecosystem (Go) - renderer with word wrap, built-in styles (dark, light, dracula...), custom styles via JSON and lipgloss/bubbletea integration. Use when a vault Go TUI needs to display formatted markdown (kanban cards, INBOX, specs, notes) with headings, lists, highlighted code and tables.
---

# charm-glamour

## What it is / when to use

glamour is the terminal markdown rendering library of the Charm ecosystem: it takes a markdown string and returns a styled ANSI string (headings, lists, blockquotes, code with highlighting via Chroma, tables). In the vault's Go TUIs (epochs 1–3), it is the piece that displays the real content — kanban cards, INBOX, specs and notes are all markdown. Use it whenever the View of a bubbletea program needs to show formatted markdown instead of raw text.

## Installation and imports

```bash
go get charm.land/glamour/v2
```

```go
import (
    "charm.land/glamour/v2"         // renderer
    "charm.land/glamour/v2/ansi"    // ansi.StyleConfig (custom style in Go)
)
```

Legacy v1 uses `github.com/charmbracelet/glamour`; new projects use v2 (`charm.land/.../v2`).

## Core concepts

- **`TermRenderer`** — the central object: create it once with `glamour.NewTermRenderer(opts...)` and reuse it by calling `r.Render(markdown) (string, error)`. Reuse the renderer; do not recreate it on every render.
- **Functional options** — every configuration is a `TermRendererOption`: `WithWordWrap(n)` (wrap width, default 80), `WithStandardStyle("dark")`, `WithStylePath(pathOrName)`, `WithStylesFromJSONFile/Bytes`, `WithStyles(ansi.StyleConfig{...})`, `WithEmoji()`, `WithPreservedNewLines()`, `WithBaseURL()` (resolves relative links).
- **Built-in styles** — names accepted where a style is requested: `dark`, `light`, `ascii`, `notty`, `pink`, `dracula`, `tokyo-night` (and `auto` in v1).
- **One-call shortcut** — `glamour.Render(in, "dark")` and `glamour.RenderWithEnvironmentConfig(in)` create a disposable renderer; good for one-shot CLIs, bad inside a TUI.
- **`GLAMOUR_STYLE`** — environment variable with a style name or JSON path; enabled via `WithEnvironmentConfig()`.
- **Pure renderer** — v2 does not detect the terminal nor downsample colors: same input, same output. Downsampling happens at print time, via lipgloss (see composition).

## Code patterns

### Quick render (one-shot CLI)

```go
in := "# Kanban\n\n- **1.1.1** example card\n"
out, err := glamour.Render(in, "dark")
if err != nil {
    // fallback: show the raw markdown
    out = in
}
fmt.Print(out)
```

### Reusable renderer with width (TUI)

```go
r, err := glamour.NewTermRenderer(
    glamour.WithStandardStyle("dark"),
    glamour.WithWordWrap(panelWidth), // never let the 80 default leak
)
if err != nil {
    return err
}
out, err := r.Render(cardContent)
```

### Render inside bubbletea (kanban card with scroll)

```go
type model struct {
    viewport viewport.Model // bubbles/viewport
    renderer *glamour.TermRenderer
    md       string
}

func (m model) Init() tea.Cmd { return nil }

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
    switch msg := msg.(type) {
    case tea.WindowSizeMsg:
        m.viewport.SetWidth(msg.Width)
        m.viewport.SetHeight(msg.Height)
        out, err := m.renderer.Render(m.md) // renderer created with WithWordWrap(msg.Width)
        if err == nil {
            m.viewport.SetContent(out)
        }
    case tea.KeyPressMsg:
        if msg.String() == "q" {
            return m, tea.Quit
        }
    }
    var cmd tea.Cmd
    m.viewport, cmd = m.viewport.Update(msg)
    return m, cmd
}

func (m model) View() tea.View { return tea.NewView(m.viewport.View()) }
```

### Color downsampling at print time (v2)

```go
out, err := r.Render(in)
if err != nil {
    return err
}
lipgloss.Print(out) // adapts colors to the terminal's capabilities
```

## Composition with the other Charm libs

glamour returns a **ready-made ANSI string** — the rest of the stack displays it: a bubbles `viewport` provides scrolling inside bubbletea, and lipgloss positions/frames the result next to other panels and does the color downsampling at print time. The width passed to `WithWordWrap` must be the real width of the lipgloss/viewport panel where the text will appear, not the whole terminal's.

## Common pitfalls

- **80-column default:** without `WithWordWrap`, text wraps at 80 even in a 40- or 200-wide panel — always pass the real panel width and recreate/reconfigure the renderer on `tea.WindowSizeMsg`.
- **Re-render on every frame:** `View()` runs on every update; rendering markdown there is waste. Render only when content or width changes and store the output in the Model.
- **Pure renderer in v2:** `WithAutoStyle`/`WithColorProfile` (v1) do not exist in v2 — choose `dark`/`light` yourself and downsample with `lipgloss.Print`/`lipgloss.Render`.
- **`WithStylePath` tries a file first:** a name that matches a file on disk is read as a style JSON, not as a built-in style.
- **Sneaky `GLAMOUR_STYLE`:** with `WithEnvironmentConfig()`, the user's environment overrides the application's style — avoid it in a TUI with its own visual identity.
- **Output already has margins:** built-in styles add margin and block breaks; stacking generous lipgloss padding on top of that squeezes the text.

## Official links

- Repo: <https://github.com/charmbracelet/glamour>
- Charm docs: <https://charm.land>
- v2 API: <https://pkg.go.dev/charm.land/glamour/v2>
- Built-in styles (source): <https://pkg.go.dev/charm.land/glamour/v2/styles>
