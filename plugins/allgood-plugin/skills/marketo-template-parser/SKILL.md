---
name: marketo-parser
description: Parse and validate Marketo Email 2.0 templates. Extract modules, variables, and structural information for large template files that exceed token limits. Includes comprehensive Marketo Email 2.0 syntax reference for answering questions about standards, validation rules, and best practices. Use for reading templates piece-by-piece, validating structure, documenting template usage, and learning Marketo syntax.
---

# Marketo Template Parser Skill

## Overview

This skill provides Python-based tools for parsing and validating Marketo Email 2.0 templates, plus comprehensive reference documentation. It solves the problem of working with large templates (4,000-5,000 lines) that exceed token limits by allowing you to:

1. **Read templates incrementally** - Get module index, then extract specific modules one at a time
2. **Validate template structure** - Check against Marketo Email 2.0 standards
3. **Extract variables** - List all customization variables without reading entire file
4. **Generate machine-readable registries** - Produce JSON module registry for downstream tools
5. **Answer Marketo questions** - Reference complete syntax documentation for elements, attributes, and validation rules

For setup and usage guidance, see `references/getting-started.md`.

## Prerequisites

Python 3 and beautifulsoup4. Install with: `pip3 install beautifulsoup4`

## Available Scripts

### 1. list_modules.py - Get Module Index

Get a quick index of all modules (IDs, names, line numbers) as JSON.

```bash
python3 scripts/list_modules.py <template.html>
python3 scripts/list_modules.py <template.html> --no-line-numbers
```

Output: JSON array of modules

```json
[
  { "id": "logo", "name": "Logo", "line": 496 },
  { "id": "hero1", "name": "Hero 1", "line": 941 }
]
```

Options:
- `--no-line-numbers` - Exclude line numbers from output

### 2. get_module.py - Extract Specific Module

Extract the complete HTML content for one specific module, or a JSON summary.

```bash
python3 scripts/get_module.py <template.html> <module_id>
python3 scripts/get_module.py <template.html> <module_id> --no-styles
python3 scripts/get_module.py <template.html> <module_id> --summary
```

Options:
- `--no-styles` - Strip `<style>` tags to reduce token usage
- `--summary` - Return JSON summary instead of full HTML

Summary output includes editable element details and variable metadata:

```json
{
  "id": "hero1",
  "name": "Hero 1",
  "line": 941,
  "add_by_default": false,
  "editable_elements": 3,
  "editable_types": ["cta", "mktoText"],
  "editable_details": [
    { "id": "hero1Btn", "type": "cta", "name": "Button" },
    { "id": "hero1Headline", "type": "mktoText", "name": "Headline" }
  ],
  "variable_references": ["bg_color_grey", "btn_bgcolor", ...],
  "variable_details": [
    { "id": "bg_color_grey", "type": "mktoColor", "default": "#f5f5f5" },
    { "id": "btn_bgcolor", "type": "mktoColor", "default": "#6837ef" }
  ],
  "html_size": 1200,
  "html_lines": 35
}
```

### 3. list_variables.py - List All Variables

Get all variable declarations from `<head>` as JSON.

```bash
python3 scripts/list_variables.py <template.html>
python3 scripts/list_variables.py <template.html> --type mktoColor
python3 scripts/list_variables.py <template.html> --scope global
```

Options:
- `--type <type>` - Filter by variable type (mktoString, mktoColor, mktoBoolean, mktoNumber, mktoList, mktoHTML, mktoImg)
- `--scope <scope>` - Filter by scope (global or module)

Output format:

```json
{
  "global": [
    { "id": "global_preheader", "type": "mktoString", "name": "Preheader", "default": "", "line": 26 }
  ],
  "module": [
    { "id": "bg_color_white", "type": "mktoColor", "name": "BG Color", "default": "#FFFFFF", "line": 47 }
  ]
}
```

### 4. validate.py - Validate Template Structure

Validate template against Marketo Email 2.0 standards and identify structural issues.

```bash
python3 scripts/validate.py <template.html>
```

Validation checks:

**Critical errors:**
- Exactly one `mktoContainer` element
- All IDs are unique (no duplicates)
- ID format valid (letters, numbers, dash, underscore only)
- Required attributes present (mktoName on modules and editable elements)

**Warnings:**
- Lowercase attribute names (`mktoname` vs `mktoName`)
- Unused variables (declared but not referenced)
- Missing default values

Output format:

```json
{
  "valid": true,
  "score": 65,
  "errors": [],
  "warnings": [
    { "type": "case_sensitivity", "message": "Found 'mktoname' on line 27 (should be 'mktoName')", "line": 27 }
  ],
  "stats": {
    "modules": 57,
    "variables": 79,
    "unique_ids": 341,
    "editable_elements": 170,
    "containers": 1
  }
}
```

Score: starts at 100, -10 per error, -1 per warning. Valid if no errors.

### 5. generate_registry.py - Generate JSON Module Registry

Pure data extraction script. Produces a machine-readable JSON registry mapping each module to its editable elements and variable references. Output schema matches `email-variant-generator/module-registry.json`.

```bash
python3 scripts/generate_registry.py <template.html>
# Writes: <template>-registry.json
```

Output schema:

```json
{
  "<moduleId>": {
    "addByDefault": true,
    "elements": { "<htmlId>": "<elementType>" },
    "content_variables": ["<varName>", ...],
    "style_variables": ["<varName>", ...]
  }
}
```

- `addByDefault` - whether the module appears on the canvas when creating a new email (`true`) or must be dragged in from the sidebar (`false`). Mirrors the `mktoAddByDefault` HTML attribute; Marketo defaults to `true` when omitted.
- `elements` - the editable content areas (mktoText, mktoImg, cta, etc.). This is where most per-email customization happens.
- `content_variables` - variables that typically need to be set per-email (background image URLs, button link targets, preheader text). Usually 0-1 per module.
- `style_variables` - colors, padding, font sizes, border radii, layout utilities. All have sensible defaults; rarely changed per-email.

Built-in validation runs automatically after generation:
- Module count matches `list_modules.py` output
- Every module name from `list_modules.py` appears in the registry
- Element counts per module match `get_module.py --summary` output
- Prints a summary: `"Validated: 57 modules, 170 elements, registry OK"` or error details

### 6. detect_version.py - Detect Template Version

Auto-detect whether a template is Email 1.0 or 2.0. For v1.0 templates, lists all `mktEditable` regions, extracts `{{my.Token}}` references, and provides upgrade guidance for migrating to Email 2.0.

```bash
python3 scripts/detect_version.py <template.html>
```

Output for v1.0 templates includes:
- `version`: `"1.0"` or `"2.0"`
- `regions`: array of `mktEditable` sections with IDs, token references, and line numbers
- `tokens`: all `{{my.Token}}` names used across the template
- `upgrade`: step-by-step migration guidance and per-region v2.0 conversion suggestions

For v2.0 templates, returns `{"version": "2.0"}` and directs to `list_modules.py` / `validate.py`.

**Run this first on any unknown template** to determine which scripts to use next.

### 7. lint_email.py - Email HTML Linter

Lint any email HTML for rendering issues across Outlook, Gmail, Apple Mail, dark mode, and accessibility. Works on any email HTML (v1.0, v2.0, or plain email — not Marketo-specific). 40 rules in 10 categories.

```bash
python3 scripts/lint_email.py <email.html>
python3 scripts/lint_email.py <email.html> --category accessibility outlook
python3 scripts/lint_email.py <email.html> --category gmail darkmode
```

Categories: `structure`, `images`, `styles`, `links`, `tables`, `accessibility`, `size`, `outlook`, `gmail`, `darkmode`

Output: JSON with issues array, summary counts, and score (100 - 5/error - 2/warning).

For details on what each rule checks and why, see `references/email-rendering-rules.md`.

---

## Workflow: Generate Reference Documentation

Use this workflow to produce human-readable reference docs for any Marketo template. The LLM drives the process, making the workflow template-agnostic.

1. Run `list_modules.py` to get the module index (JSON array of `{id, name, line}`)
2. Run `generate_registry.py` to get the machine-readable registry JSON
3. For each module (or in batches), use a subagent (smaller model) that:
   a. Receives the full module HTML via `get_module.py <id>`
   b. Also receives the `--summary` data (elements, variables, add_by_default)
   c. Returns a structured description: what the module does, what's editable, what's decorative, typical use cases
4. Assemble the reference docs:
   - `<template>-reference.md`: overview table (module ID, name, editable types, LLM-generated description, add_by_default)
   - `<template>-details.md`: full specs per module (elements with htmlIds/types, variables with types/defaults, LLM-generated description)
5. Cross-validate: module count in `reference.md` = count in `registry.json`, all module names match between the three artifacts

---

## Other Workflows

### Read Large Template Piece-by-Piece

```bash
# Step 1: Get module index (small JSON output)
python3 scripts/list_modules.py template.html > modules.json

# Step 2: Read modules.json to see what's available

# Step 3: Extract specific module for analysis
python3 scripts/get_module.py template.html hero1 > hero1.html

# Step 4: Analyze hero1.html (only ~25 lines instead of 4,697)
```

### Validate Template Quality

```bash
python3 scripts/validate.py template.html

# Get validation summary
python3 scripts/validate.py template.html | jq '{valid, score, errors: .errors | length, warnings: .warnings | length}'
```

### Document Template Usage

```bash
# Get all modules
python3 scripts/list_modules.py template.html > modules.json

# Get all variables
python3 scripts/list_variables.py template.html > variables.json

# Get validation stats
python3 scripts/validate.py template.html > validation.json

# Claude reads these 3 small JSON files and generates markdown documentation
```

### Find Specific Module Type

```bash
# List all modules and filter by name
python3 scripts/list_modules.py template.html | jq '.[] | select(.name | contains("Hero"))'
```

---

## Common Questions & Reference Usage

**"What attributes can I use on mktoImg elements?"**
- Read `references/marketo-template-reference.md` (Section 2.4 mktoImg)

**"What modules are available in the template?"**
- Run `python3 scripts/list_modules.py <template.html>`

**"What variables does the hero1 module use?"**
- Run `python3 scripts/get_module.py <template.html> hero1 --summary`

**"Why is my template validation failing?"**
- Read `references/validation_rules.md` (validation criteria)

**"Can I nest modules inside modules?"**
- Read `references/marketo-template-reference.md` (Section 3.1 - Critical Constraints)

**"Will this email render correctly in Outlook/Gmail?"**
- Run `python3 scripts/lint_email.py <email.html>`

**"What are the dark mode / accessibility issues?"**
- Run `python3 scripts/lint_email.py <email.html> --category darkmode accessibility`
- Read `references/email-rendering-rules.md` for client-specific details

## Reference Files

### General Marketo Knowledge

**`references/marketo-template-reference.md`** - Complete Marketo Email 2.0 syntax reference
- Full syntax documentation for all Marketo elements (mktoModule, mktoText, mktoImg, etc.)
- Validation rules and critical constraints
- Best practices and common patterns

**`references/validation_rules.md`** - Validation criteria for templates
- Critical errors (container rules, ID uniqueness, required attributes)
- Non-critical warnings (case sensitivity, unused variables)

**`references/email-rendering-rules.md`** - Email HTML rendering rules by client
- Outlook Word engine constraints and workarounds (ghost tables, VML, padding rules)
- Gmail sanitizer rules (8KB style limit, 102KB clip, background-image stripping)
- Apple Mail dark mode opt-in, auto-link prevention
- Dark mode client matrix (no-change / partial / full invert)
- WCAG accessibility requirements for email
- Responsive hybrid/spongy layout patterns

**`references/getting-started.md`** - Setup and usage guide

### Template-Specific References (Generated)

When you generate a registry or reference docs for a template, you get:

**`<template>-registry.json`** - Machine-readable module registry
- Maps each module ID to its elements and variables
- Compatible with `email-variant-generator/module-registry.json` schema

**`<template>-reference.md`** - Quick overview (generated by LLM workflow)
- Table of all modules with descriptions

**`<template>-details.md`** - Full specifications (generated by LLM workflow)
- Complete variable lists per module with types and defaults

## Notes

- **Case sensitivity:** Marketo allows lowercase attributes (`mktoname`), but camelCase (`mktoName`) is recommended for consistency
- **Warnings vs Errors:** Errors prevent template from working; warnings are best-practice violations
- **Line numbers:** All scripts include line numbers for easy navigation to issues
- **JSON output:** All scripts output JSON for easy parsing and filtering with `jq`
