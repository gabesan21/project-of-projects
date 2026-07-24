---
name: charm-huh
description: Usage contract for the huh library (Charm) to build interactive terminal forms and prompts in Go - forms, groups, fields, validation, themes, spinner and Bubble Tea integration. Use when a vault Go TUI task needs to collect user input (task selection, action confirmation, field editing) or embed a form in a bubbletea program.
---

# charm-huh

**Principle: declare the form, not the loop.** You describe groups and fields with bindings to variables; huh takes care of navigation, validation, help and rendering on top of Bubble Tea.

## What it is / when to use

huh is the terminal forms library of the Charm ecosystem (same family as bubbletea, lipgloss, bubbles and glamour). Use it in the vault's Go TUIs (epochs 1–3) for every input interaction: picking a task from the kanban, confirming a stage transition, filling in card fields. For pure display (lists, rendered markdown), prefer bubbles + glamour; huh is for **collecting** data.

## Installation and imports

```bash
go get charm.land/huh/v2
```

```go
import (
    "charm.land/huh/v2"
    "charm.land/huh/v2/spinner" // standalone spinner (post-submit feedback)
)
```

v2 is the current line (module `charm.land/huh/v2`). Legacy v1 lives at `github.com/charmbracelet/huh` — do not mix the two in the same module.

## Core concepts

- **Form** — the whole form: a collection of groups displayed one at a time ("pages"). `huh.NewForm(groups...)`, runs with `form.Run()`.
- **Group** — one page of the form: `huh.NewGroup(fields...)`. The form only advances past a group when all fields validate.
- **Field** — a control: `Input` (single line), `Text` (multi-line, opens `$EDITOR`), `Select[T]` / `MultiSelect[T]` (generics), `Confirm` (yes/no), `Note` (only displays text/markdown), `FilePicker`. Every field is a `tea.Model`.
- **Binding** — `.Value(&variable)` links the field to one of your variables; at the end of the form it is filled in. Alternative: `.Key("name")` + `form.GetString("name")` afterwards.
- **Option** — `huh.NewOption("visible label", value)` or `huh.NewOptions(values...)`; the value can be any comparable type.
- **Validation** — `.Validate(func(v T) error)`; ready-made: `huh.ValidateNotEmpty()`, `huh.ValidateMinLength(n)` etc.
- **Dynamic** — `TitleFunc`/`OptionsFunc`/`DescriptionFunc(f, &binding)` recompute (with cache) when the binding changes.
- **Theme** — `form.WithTheme(...)`; ready-made: Charm, Catppuccin, Dracula, Base16 (`huh.ThemeCharm`, …, functions `func(isDark bool) *Styles`).
- **State** — `form.State`: `huh.StateNormal`, `huh.StateCompleted`, `huh.StateAborted`.

## Code patterns

Complete standalone form (most common case: collect and move on):

```go
var (
    task    string
    confirm bool
)

form := huh.NewForm(
    huh.NewGroup(
        huh.NewSelect[string]().
            Title("Which task to advance?").
            Options(
                huh.NewOption("1.1.1-setup-core", "1.1.1-setup-core"),
                huh.NewOption("1.1.2-models", "1.1.2-models"),
            ).
            Value(&task),
    ),
    huh.NewGroup(
        huh.NewConfirm().
            Title("Confirm advance to 002_planning?").
            Affirmative("Yes").
            Negative("No").
            Value(&confirm),
    ),
)

err := form.Run()
if err != nil {
    log.Fatal(err) // see the ErrUserAborted pitfall
}
```

Single prompt (shortcut without an explicit Form — `Run()` blocks):

```go
var name string
err := huh.NewInput().
    Title("Slug of the new task?").
    Validate(huh.ValidateNotEmpty()).
    Value(&name).
    Run()
```

Dynamic form (options recomputed when another field changes — note the `&country` binding):

```go
huh.NewSelect[string]().
    Title("State").
    OptionsFunc(func() []huh.Option[string] {
        return huh.NewOptions(statesFor(country)...)
    }, &country). // without this binding, recomputes on every keystroke
    Value(&state)
```

huh inside a Bubble Tea program (`*huh.Form` is a `tea.Model` — delegate Init/Update/View):

```go
func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
    if m.form.State == huh.StateCompleted {
        return m, tea.Quit // value is already in the binding or in m.form.GetString("key")
    }
    form, cmd := m.form.Update(msg)
    if f, ok := form.(*huh.Form); ok {
        m.form = f
    }
    return m, cmd
}
```

Post-submit spinner (feedback for a slow action, e.g. calling a `pop_*` script):

```go
err := spinner.New().
    Title("Moving task on the kanban...").
    Action(func() { runPopMove(task) }).
    Run()
```

## Composition with the other Charm libs

huh is built on top of Bubble Tea — standalone via `form.Run()` or embedded as a `tea.Model` in a larger app (as the vault TUIs will do). huh themes are lipgloss styles (`huh.ThemeCharm(isDark)` etc.). `form.WithProgramOptions(...)` accepts `tea.ProgramOption` — but in bubbletea v2 there is **no** alt screen option: for a full-screen form, embed the `*huh.Form` in a host program whose `View()` declares `v.AltScreen = true` (pattern above). Markdown displayed in `Note`/descriptions can be pre-rendered with glamour before becoming a string.

## Common pitfalls

- **`form.Run()` returns `huh.ErrUserAborted`** when the user exits with esc/ctrl+c before submitting — treat it as a normal cancellation, not as a generic `log.Fatal`.
- **Forgetting the `&` in `.Value(&var)`** does not compile (good), but forgetting `.Value`/`.Key` leaves the value trapped in the form — every input field needs a binding or a key.
- **`Select`/`MultiSelect` are generic:** declare the type (`huh.NewSelect[string]()`) and remember that `NewOption(label, value)` separates the visible text from the stored value.
- **`OptionsFunc` without the correct binding** (second argument) loses the cache and re-runs the function on every input — on a function that hits disk/network this freezes the form.
- **Validation is per group:** one invalid field blocks the entire page from advancing; error messages only appear with `WithShowErrors(true)` (default) — do not turn it off without a reason.
- **Accessibility:** `form.WithAccessible(os.Getenv("ACCESSIBLE") != "")` swaps the TUI for simple prompts for screen readers; `WithTimeout` does not work in accessible mode (`ErrTimeoutUnsupported`).

## Official links

- Repo: https://github.com/charmbracelet/huh — complete examples in `examples/` (dynamic, bubbletea, spinner).
- Charm docs: https://charm.land — guide and theme reference.
- API: https://pkg.go.dev/charm.land/huh/v2 — complete reference of fields, keymaps and layouts.
