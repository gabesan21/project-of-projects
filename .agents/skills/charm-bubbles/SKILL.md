---
name: charm-bubbles
description: Usage contract for the Bubbles library (charm.land/bubbles/v2) — ready-made TUI components (list, viewport, textinput, spinner, progress, table, paginator, help, key) for Bubble Tea. Use when coding or reviewing the vault's Go TUIs (kanban/INBOX reading, actions TUI) and you need to build interactive screens with the official Charm components.
---

# charm-bubbles

## What it is / when to use

Bubbles is the official collection of UI components for Bubble Tea — each component (a "bubble") is a ready-made `tea.Model`: navigable list, scrolling viewport, inputs, spinner, progress bar etc. Use it in every code task of the vault's TUIs (epochs 2 and 3 of the [[ROADMAP|ROADMAP]]): kanban/INBOX reading calls for `list` + `viewport` + `glamour`; actions (move card, create task) call for `textinput`/`textarea`, `spinner` and `help`. This skill covers **v2** (`charm.land/bubbles/v2`), which requires Bubble Tea v2 and Lip Gloss v2 — v1 docs and examples (`github.com/charmbracelet/bubbles`) are outdated; do not copy their API.

## Installation and imports

```sh
go get charm.land/bubbles/v2@latest
go get charm.land/bubbletea/v2@latest
go get charm.land/lipgloss/v2@latest
```

Each component is its own subpackage — import only what you use:

```go
import (
    tea "charm.land/bubbletea/v2"
    "charm.land/bubbles/v2/help"
    "charm.land/bubbles/v2/key"
    "charm.land/bubbles/v2/list"
    "charm.land/bubbles/v2/paginator"
    "charm.land/bubbles/v2/progress"
    "charm.land/bubbles/v2/spinner"
    "charm.land/bubbles/v2/table"
    "charm.land/bubbles/v2/textarea"
    "charm.land/bubbles/v2/textinput"
    "charm.land/bubbles/v2/viewport"
    "charm.land/lipgloss/v2"
)
```

## Core concepts

- **Component = `tea.Model`:** every bubble has `Init()`, `Update(msg) (Model, tea.Cmd)` and `View() string`. The host model embeds the bubbles as fields, forwards messages in `Update` and concatenates the `View()`s in the layout.
- **`key.Binding` is the key contract:** declare your own `KeyMap` with `key.NewBinding(key.WithKeys(...), key.WithHelp(...))`, test with `key.Matches(msg, binding)` and serve the same map to `help` — keys and help never diverge.
- **Own messages:** each bubble has its own msg types (`spinner.TickMsg`, `progress.FrameMsg`). Animation only advances if you return the component's `tea.Cmd`.
- **Construction by options:** `viewport.New(viewport.WithWidth(80))`, `spinner.New(spinner.WithSpinner(spinner.Dot))`. Size is adjusted with `SetWidth`/`SetHeight`/`SetSize` (exported `Width`/`Height` fields no longer exist in v2).
- **Explicit light/dark styles:** v2 does not detect the terminal background — `DefaultStyles(isDark bool)` in `list`, `help`, `textinput`, `textarea`. Get `isDark` with `tea.RequestBackgroundColor` (response in `tea.BackgroundColorMsg`) or `lipgloss.HasDarkBackground(os.Stdin, os.Stdout)` (a function at the lipgloss v2 root; in the `compat` subpackage it is a variable, not a function).

## Code patterns

### Navigable list (kanban reading)

```go
type card struct{ title, stage string }

func (c card) Title() string       { return c.title }
func (c card) Description() string { return c.stage }
func (c card) FilterValue() string { return c.title } // enables fuzzy filter

items := []list.Item{card{title: "1.1.1-setup", stage: "004_processing"}}
l := list.New(items, list.NewDefaultDelegate(), 0, 0)
l.Title = "Kanban"
// host Update:
//   case tea.WindowSizeMsg: m.list.SetSize(msg.Width, msg.Height)
//   m.list, cmd = m.list.Update(msg)   // forwards ALL msgs
```

### Viewport with rendered content (markdown via glamour)

```go
vp := viewport.New(viewport.WithWidth(80), viewport.WithHeight(24))
vp.SetContent(renderedMarkdown) // ANSI string from glamour
// vp.SoftWrap = true           // optional soft wrap
// Update: m.viewport, cmd = m.viewport.Update(msg)  // keyboard/mouse scroll
```

### Spinner + async Cmd (action in progress)

```go
s := spinner.New(spinner.WithSpinner(spinner.Dot))
// host Init: return tea.Batch(m.spinner.Tick, myAsyncCmd)
// Update:
case spinner.TickMsg:
    var cmd tea.Cmd
    m.spinner, cmd = m.spinner.Update(msg)
    return m, cmd
```

### Keys + help (any screen)

```go
type keyMap struct{ Quit key.Binding }

var keys = keyMap{
    Quit: key.NewBinding(key.WithKeys("q", "ctrl+c"), key.WithHelp("q", "quit")),
}

func (k keyMap) ShortHelp() []key.Binding   { return []key.Binding{k.Quit} }
func (k keyMap) FullHelp() [][]key.Binding  { return [][]key.Binding{{k.Quit}} }

// Update: case key.Matches(msg, keys.Quit): return m, tea.Quit
// View: m.help.View(keys)  // help.New(), with m.help.SetWidth(w)
```

### Quick reference for the rest

- **textinput/textarea:** `textinput.New()`, then `ti.Placeholder`, `ti.Focus()`, `ti.CharLimit`, `ti.SetWidth(40)`; value in `ti.Value()`. `textarea` for multi-line; styles via `DefaultStyles(isDark)` + `SetStyles`.
- **progress:** `progress.New(progress.WithDefaultBlend())`; static with `p.ViewAs(0.65)`, animated by forwarding `progress.FrameMsg` in `Update`.
- **table:** `table.New(table.WithColumns([]table.Column{{Title: "Task", Width: 30}}), table.WithRows(rows), table.WithFocused(true))`; selection in `t.SelectedRow()`.
- **paginator:** `paginator.New()`, `p.Type = paginator.Dots`, `p.PerPage = 10`, `p.SetTotalPages(n)`; customize `p.KeyMap` (the `UseJKKeys` etc. toggles are gone in v2).

## Composition with the other Charm libs

Bubbles does not run alone: it requires Bubble Tea v2 (the `Model/Update/View` loop, `tea.Cmd`, `tea.KeyPressMsg`) and is styled with Lip Gloss v2. glamour generates the ANSI string of the vault's markdown and the `viewport` displays it — the glamour renderer's width must match the viewport's. For complete declarative forms (`new-task` wizard), consider `huh` instead of composing `textinput` by hand.

## Common pitfalls

- **Forgetting to forward msgs:** if the host's `Update` does not pass the msg to the bubble (or discards the returned `tea.Cmd`), the spinner freezes, the list does not filter and progress does not animate.
- **Ghost v1 API:** `tea.KeyMsg` (→ `tea.KeyPressMsg`), `NewModel()` (→ `New()`), `DefaultKeyMap` variable (→ function), direct `Width`/`Height` fields (→ setters) are v1 — v2 breaks on all of them; official guide in `UPGRADE_GUIDE_V2.md` in the repo.
- **Blocking the loop:** never do I/O or `time.Sleep` in `Update` — slow work goes in a `tea.Cmd` (async), with `spinner`/`progress` giving feedback.
- **Broken ANSI in the viewport:** glamour content wider than the viewport cuts escape sequences when wrapping; match the renderer's width to the viewport's (or `SoftWrap` + reflow).
- **Alt screen is a `tea.View` field, not a ProgramOption:** in v2 there is **no** `tea.WithAltScreen()` (ghost v1 API). Full screen is declared in the host model's `View()`: `v := tea.NewView(content); v.AltScreen = true; return v`. Full-screen TUIs (list + viewport) need this to avoid polluting the scrollback; simple inline inputs do not.

## Official links

- Repo: <https://github.com/charmbracelet/bubbles> (per-component examples in each subpackage)
- Docs/API: <https://pkg.go.dev/charm.land/bubbles/v2>
- v1→v2 migration guide: <https://github.com/charmbracelet/bubbles/blob/main/UPGRADE_GUIDE_V2.md>
- Charm: <https://charm.land>
