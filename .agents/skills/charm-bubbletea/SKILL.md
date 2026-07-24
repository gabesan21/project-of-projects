---
name: charm-bubbletea
description: Usage contract for the Charm ecosystem for Go TUIs (bubbletea, lipgloss, bubbles, huh, glamour) - mental model, v2 imports, code patterns and pitfalls. Use when creating or changing any Go TUI code in the vault (core, kanban/INBOX reading TUI, actions TUI), including rendering vault markdown in the terminal with glamour.
---

# charm-bubbletea

## What it is / when to use

Charm's official Go TUI stack. `bubbletea` is the runtime (Elm Architecture), `lipgloss` styles and assembles layout, `bubbles` provides ready-made components, `huh` builds forms and `glamour` renders markdown in the terminal. It is the stack of the vault's Go TUIs (core + kanban/INBOX reading + actions); glamour is the key piece for displaying the vault's markdown files. Read this skill before coding any TUI — then follow the official docs of the lib you will use.

## Installation and imports

The libs migrated to `charm.land` with major `v2` (the GitHub repos remain `charmbracelet/<lib>`). Current imports:

```go
go get charm.land/bubbletea/v2   // runtime: tea
go get charm.land/lipgloss/v2    // style and layout
go get charm.land/bubbles/v2     // components (spinner, list, viewport, textinput...)
go get charm.land/huh/v2         // forms and prompts
go get charm.land/glamour/v2     // markdown in the terminal
```

## Core concepts

- **bubbletea** — Elm Architecture: `Model` (state, usually a value struct) with 3 methods: `Init() tea.Cmd` (initial I/O), `Update(tea.Msg) (tea.Model, tea.Cmd)` (reacts to events) and `View() tea.View` (declares the UI; the runtime redraws). `Msg` is any type (key = `tea.KeyPressMsg`, resize = `tea.WindowSizeMsg`); `Cmd` is `func() tea.Msg` — all async I/O lives in Cmds, never in the Update body. `tea.Quit` exits.
- **lipgloss** — immutable, chainable `lipgloss.NewStyle()` (Bold, Foreground, Padding, Border...); `Style.Render(s)` produces an ANSI string. Layout with `JoinHorizontal`/`JoinVertical`/`Place`; measurement with `lipgloss.Width/Height/Size`. Colors: `lipgloss.Color("63")` (256) or `"#7D56F4"` (truecolor); downsampling to the terminal profile is automatic.
- **bubbles** — components that are Models: they have their own `Update`/`View`; you embed them in your Model, delegate the `msg` in Update and concatenate the Cmds. `spinner`, `list`, `viewport`, `textinput`, `table`, `progress`, `paginator`, `help`, `key` (bindings with `key.Matches`).
- **huh** — `huh.NewForm(huh.NewGroup(fields...))` (Group = page); fields: `NewInput`, `NewText`, `NewSelect[T]`, `NewMultiSelect[T]`, `NewConfirm`, with `Value(&var)`, `Validate(fn)` and `Options(huh.NewOption(label, value))`. Standalone via `form.Run()`; embedded, `huh.Form` is a `tea.Model`.
- **glamour** — renders markdown to ANSI: shortcut `glamour.Render(md, "dark")` or `glamour.NewTermRenderer(glamour.WithWordWrap(w))` + `r.Render(md)`. Ready-made styles ("dark", "light", "notty"...) or your own stylesheet; `GLAMOUR_STYLE` as env.

## Code patterns

Minimal bubbletea v2 program (`q` key quits; alt screen is a View field):

```go
package main

import (
	"fmt"

	tea "charm.land/bubbletea/v2"
)

type model struct{ count int }

func (m model) Init() tea.Cmd { return nil }

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyPressMsg:
		switch msg.String() {
		case "ctrl+c", "q":
			return m, tea.Quit
		}
	}
	return m, nil
}

func (m model) View() tea.View {
	v := tea.NewView(fmt.Sprintf("Hello, vault!\n\nq: quit\n"))
	v.AltScreen = true // full screen; in v2 there is no tea.WithAltScreen
	return v
}

func main() {
	if _, err := tea.NewProgram(model{}).Run(); err != nil {
		fmt.Println("error:", err)
	}
}
```

Rendering vault markdown with glamour (real width = viewport minus lipgloss border/padding):

```go
import "charm.land/glamour/v2"

r, _ := glamour.NewTermRenderer(
	glamour.WithStandardStyle("dark"),
	glamour.WithWordWrap(width), // default is 80: adjust to the real width
)
out, err := r.Render(markdownString)
```

Standalone huh form (useful for confirmations and inputs in the actions TUI):

```go
import "charm.land/huh/v2"

var stage string
var confirm bool

form := huh.NewForm(huh.NewGroup(
	huh.NewSelect[string]().
		Title("Move task to").
		Options(huh.NewOptions("002_planning", "004_processing")...).
		Value(&stage),
	huh.NewConfirm().Title("Confirm?").Value(&confirm),
))
err := form.Run()
```

Style and layout with lipgloss (bordered block for kanban cards):

```go
import "charm.land/lipgloss/v2"

card := lipgloss.NewStyle().
	Border(lipgloss.RoundedBorder()).
	BorderForeground(lipgloss.Color("63")).
	Padding(0, 1).Width(40).
	Render(title + "\n" + description)
```

Embedded bubbles spinner (embedding = delegating Update and concatenating Cmd):

```go
import "charm.land/bubbles/v2/spinner"

type model struct{ sp spinner.Model }

func (m model) Init() tea.Cmd { return m.sp.Tick } // starts the animation

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	var cmd tea.Cmd
	m.sp, cmd = m.sp.Update(msg)
	return m, cmd
}
```

## Composition between the libs

bubbles and huh are bubbletea Models — they run inside your `Update`/`View`. lipgloss styles everything (strings that go into the `tea.View` and into huh themes). The vault's reading pipeline is: file markdown → glamour (ANSI string) → lipgloss (frame/position) → bubbletea displays, usually inside a bubbles `viewport` for scrolling.

## Common pitfalls

- **v1 vs v2:** in v2 `View()` returns `tea.View` (not string), alt screen is `v.AltScreen = true` (there is no `tea.WithAltScreen`), a key is `tea.KeyPressMsg` and imports are `charm.land/<lib>/v2`. Old examples from the web break — check the major before copying.
- **Never do I/O or heavy processing in Update:** the loop freezes and the UI locks up. File reading, parsing and external calls become a `tea.Cmd` that returns a `Msg` with the result.
- **glamour width:** the default wrap is 80 columns. Pass `WithWordWrap` with the real usable width (viewport − lipgloss border − padding), otherwise the content overflows or wraps twice.
- **glamour does not downsample colors** (the renderer is pure): outside bubbletea, print the output via `lipgloss.Print` to respect the terminal's color profile. With bubbletea v2, downsampling is built in.
- **Forgotten component freezes:** when embedding a bubble/huh, every `msg` must reach the child's `Update` and every `Cmd` from it must be returned (combine with `tea.Batch` when there is more than one).

## Official links

- bubbletea: [repo](https://github.com/charmbracelet/bubbletea) · [pkg.go.dev](https://pkg.go.dev/charm.land/bubbletea/v2)
- lipgloss: [repo](https://github.com/charmbracelet/lipgloss) · [pkg.go.dev](https://pkg.go.dev/charm.land/lipgloss/v2)
- bubbles: [repo](https://github.com/charmbracelet/bubbles) · [pkg.go.dev](https://pkg.go.dev/charm.land/bubbles/v2)
- huh: [repo](https://github.com/charmbracelet/huh) · [pkg.go.dev](https://pkg.go.dev/charm.land/huh/v2)
- glamour: [repo](https://github.com/charmbracelet/glamour) · [pkg.go.dev](https://pkg.go.dev/charm.land/glamour/v2)
- Charm portal: [charm.land](https://charm.land)
