---
name: marketo-template-parser
description: Work with Marketo Email 2.0 templates — parse, validate, lint for client-rendering issues, and edit. Use when the user asks about Marketo templates, wants to review quality, fix a template issue, add or modify modules, check Outlook/Gmail/dark-mode rendering, or answer Email 2.0 syntax questions. Handles large templates (4,000+ lines) via incremental parsing scripts, and can fetch email HTML directly from Marketo via MCP to read and write changes. Use this skill whenever the user mentions Marketo templates, mktoModule, mktoContainer, mktoText/mktoImg, email HTML rendering quirks, or shares an `.html` file that looks like a Marketo template — even if they don't explicitly ask to "parse" it.
---

# Marketo Template Parser

A toolkit of Python scripts and references for working with Marketo Email 2.0 templates. Templates are often 4,000–5,000 lines — these scripts let you extract modules, variables, and structural info without reading the entire file. The references explain Marketo syntax and client-rendering rules so you can answer questions and justify fixes.

Compose these pieces however the user's task calls for. The skill intentionally does not prescribe a fixed workflow — the scripts are building blocks, not a pipeline.

## Prerequisites

Python 3 and BeautifulSoup4. Either run `./setup.sh` once, or `pip3 install beautifulsoup4`.

All scripts output JSON so you can parse and filter with `jq`.

## Is this even a 2.0 template?

Run this first on an unknown template. It's a fast version gate — if the template is Email 1.0, the rest of the scripts won't apply and the model should redirect the user accordingly.

```bash
python3 scripts/detect_version.py <template.html>
```

Returns `{"version": "2.0"}` (proceed), `{"version": "1.0", "message": ..., "region_count": N, "token_count": N}` (stop — upgrade guidance is in `references/marketo-template-reference.md`), or `{"version": "unknown"}`.

## Critical Constraints (Email 2.0)

| # | Constraint | Consequence |
|---|-----------|-------------|
| 1 | Only ONE `mktoContainer` per template | "Invalid Module" error |
| 2 | Containers can ONLY contain Modules as direct children | "Invalid Module" error |
| 3 | Class names are CASE-SENSITIVE (`mktoText` not `mktotext`) | Element silently ignored |
| 4 | Custom attribute names are NOT case-sensitive (`mktoName` = `mktoname`) | Both work |
| 5 | All `id` values must be unique across entire template | Editor crash, broken CSS |
| 6 | IDs: letters, numbers, dash, underscore only | Validation failure |
| 7 | Module element type must match container type | Structural break |
| 8 | Modules cannot be nested | "Invalid Module" error |
| 9 | `mktoButton` does NOT exist in Email 2.0 | Use table-based buttons |

## Scripts (toolkit)

All scripts live in `scripts/` and output JSON.

| Script | What it does | Notable flags |
|---|---|---|
| `detect_version.py` | Email 1.0 vs 2.0 gate | — |
| `list_modules.py` | Index of all modules (`id`, `name`, `line`) | `--no-line-numbers` |
| `get_module.py` | Extract one module's HTML or a summary (elements, variables, metadata) | `--no-styles`, `--summary` |
| `list_variables.py` | All `<meta>` variable declarations | `--type <mktoType>`, `--scope global\|module` |
| `validate.py` | Validate structure against 2.0 standards. Returns `{valid, score, errors, warnings, stats}` (score starts at 100, −10 per error, −1 per warning) | — |
| `generate_registry.py` | Machine-readable JSON mapping each module → editable elements + variable references. Built-in cross-validation | Writes `<template>-registry.json` |
| `lint_email.py` | Lint email HTML for client-rendering issues (Outlook, Gmail, dark mode, accessibility). 40 rules in 10 categories. Works on any email HTML, not just Marketo | `--category structure\|images\|styles\|links\|tables\|accessibility\|size\|outlook\|gmail\|darkmode` |

Scripts compose freely. For example: pipe `list_modules.py` through `jq` to find specific modules, then `get_module.py` into `lint_email.py` to check one module in isolation.

## References (load on demand)

| File | When to load |
|---|---|
| `references/marketo-template-reference.md` | Questions about `mktoModule`, `mktoContainer`, `mktoText`, `mktoImg`, `mktoSnippet`, `mktoVideo`, element attributes, nesting rules, or Email 1.0 → 2.0 upgrade |
| `references/validation_rules.md` | Understanding validation errors, what each warning means, how to fix them |
| `references/variable-naming-conventions.md` | Questions about `<meta>` variables, scoping, `${variableId}` vs `{{my.token}}`, camelCase rules, why tokens in `href` don't resolve via fullContent API |
| `references/email-rendering-rules.md` | Questions about Outlook Word-engine quirks, Gmail 8KB style cap / 102KB clip, dark mode behavior per client, WCAG rules, responsive/hybrid patterns. Load whenever `lint_email.py` surfaces an issue the user wants explained |
| `references/marketo-mcp-tools.md` | When the user wants to pull a live email from Marketo, push edits back, or manage snippets/tokens via MCP |

## Working with live Marketo assets (via MCP)

If the user gives you an email ID or name instead of a local file, pull the HTML from Marketo directly:

1. `get_email_by_id` or `get_email_by_name` → confirm the email, capture the ID
2. `get_email_content(id)` → returns editable sections with their `htmlId`s and values
3. Analyze with the scripts above as you would a local file
4. To write a fix back: `update_email_content(id, htmlId, value)` then `approve_email(id)` — always confirm with the user first and show what's changing

**Important caveat:** MCP exposes email-level and snippet-level editing, not template-level. You can fix an individual email's content, but editing the underlying template itself still happens in the Marketo UI. Surface this when the user's ask implies template-level changes.

See `references/marketo-mcp-tools.md` for the full tool catalog (emails, snippets, tokens, impact analysis).

## Composition patterns (illustrative, not a menu)

These are *examples* of how to combine the toolkit — not the only things this skill does. Compose freely based on what the user actually wants.

**"Is this template any good?"**
- `detect_version.py` → `validate.py` → `lint_email.py` → summarize errors, warnings, and rendering issues with an overall score

**"The hero module renders weird in Outlook"**
- `list_modules.py` to locate `hero` → `get_module.py hero` → `lint_email.py --category outlook` on that module alone → explain using `references/email-rendering-rules.md` → propose a fix the user can apply

**"Add a new testimonial module"**
- `list_modules.py` to find a similar existing module → `get_module.py <similar-id>` as a pattern → draft the new module → `validate.py` to check it → user pastes it in

**"Which modules use `btn_bgcolor`?"**
- `generate_registry.py` → grep/jq the registry for that variable in `content_variables` or `style_variables`

**"Compare variables between two templates"**
- `list_variables.py` on each → diff the outputs with `jq` or by hand

**"Pull email 12345 and check it for dark mode issues"**
- `get_email_by_id(12345)` → `get_email_content(12345)` → reassemble and run `lint_email.py --category darkmode`

**"Audit all our templates"**
- Run `validate.py` and `lint_email.py` on each in a loop → aggregate scores → flag the worst offenders

**"What attributes can I use on `mktoImg`?"**
- Read `references/marketo-template-reference.md` — no scripts needed

**"Why is my validation failing?"**
- `validate.py` for the list of errors/warnings → `references/validation_rules.md` for each one's meaning and fix

## Notes

- **JSON output:** every script outputs JSON for piping and filtering with `jq`
- **Line numbers:** most scripts include line numbers so you can point the user to the exact line
- **Case sensitivity:** Marketo allows lowercase custom attributes (`mktoname`), but camelCase (`mktoName`) is the recommended convention — `validate.py` flags this as a warning, not an error
- **Warnings vs errors:** errors prevent the template from working; warnings are best-practice violations
- **Generated registry:** `generate_registry.py` runs its own cross-validation after writing the file — module counts and element counts are checked against `list_modules.py` and `get_module.py --summary` output
