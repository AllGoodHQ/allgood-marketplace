# Marketo Template Parser

Python-based toolkit for parsing, validating, and linting Marketo email templates. Works with both Email 1.0 and 2.0 templates.

## Prerequisites

- Python 3
- beautifulsoup4: `pip3 install beautifulsoup4`

## Scripts

### Template Analysis (Marketo-specific)

| Script | Purpose | Works with |
|--------|---------|------------|
| `detect_version.py` | Detect v1.0 vs v2.0, analyze structure, provide upgrade guidance | v1.0 + v2.0 |
| `list_modules.py` | List all modules (ID, name, line number) as JSON | v2.0 |
| `get_module.py` | Extract a single module's HTML or summary | v2.0 |
| `list_variables.py` | List all variable declarations from `<head>` | v2.0 |
| `validate.py` | Validate Marketo Email 2.0 structural correctness | v2.0 |
| `generate_registry.py` | Generate JSON module registry for downstream tools | v2.0 |

### Email HTML Linting (Universal)

| Script | Purpose | Works with |
|--------|---------|------------|
| `lint_email.py` | Lint email HTML for rendering issues across clients | Any email HTML |

## Quick Start

```bash
# First, detect what you're working with
python3 scripts/detect_version.py template.html

# For v2.0 templates: list modules, validate, generate registry
python3 scripts/list_modules.py template.html
python3 scripts/validate.py template.html
python3 scripts/generate_registry.py template.html

# For any email: lint for rendering issues
python3 scripts/lint_email.py template.html
python3 scripts/lint_email.py template.html --category accessibility outlook
```

## Lint Categories

The linter checks 40 rules across 10 categories:

| Category | What it checks |
|----------|----------------|
| `structure` | DOCTYPE, `<html lang>`, charset meta |
| `images` | alt attributes, HTML width/height, HTTPS, SVG |
| `links` | Missing href, javascript: links, HTTPS, visible content |
| `tables` | `role="presentation"` on layout tables, nesting depth |
| `styles` | Banned CSS (float, flex, grid), !important in inline, external sheets, JS |
| `accessibility` | Font sizes, line-height, heading hierarchy, link underlines, font fallbacks |
| `size` | Gmail 102KB clip limit |
| `gmail` | Style block limits (8KB), background-image in style, attribute selectors |
| `outlook` | Padding on `<a>`, CSS-only img sizing, VML xmlns, `<button>` elements |
| `darkmode` | Missing text/bg color pairs, pure white/black, meta+CSS pairing, PNG logos |

## Reference Files

| File | Content |
|------|---------|
| `references/marketo-template-reference.md` | Complete Marketo Email 2.0 syntax reference (elements, attributes, validation) |
| `references/validation_rules.md` | Marketo structural validation criteria (errors and warnings) |
| `references/email-rendering-rules.md` | Email HTML rendering rules by client (Outlook, Gmail, Apple Mail, dark mode, accessibility) |
| `references/getting-started.md` | Setup and usage guide |

## Example Output

### validate.py (Marketo structural)
```json
{
  "valid": true,
  "score": 65,
  "errors": [],
  "warnings": [{"type": "case_sensitivity", "message": "Found 'mktoname' (should be 'mktoName')", "line": 27}],
  "stats": {"modules": 57, "variables": 81, "editable_elements": 170, "containers": 1}
}
```

### lint_email.py (Rendering issues)
```json
{
  "issues": [
    {"id": "IMG-001", "severity": "error", "message": "<img> missing alt attribute (src: hero.jpg)"},
    {"id": "TBL-001", "severity": "warning", "message": "Layout table missing role=\"presentation\""}
  ],
  "summary": {"errors": 2, "warnings": 15, "total": 17},
  "score": 60
}
```

### detect_version.py (v1.0 analysis)
```json
{
  "version": "1.0",
  "regions": [{"id": "edit_Hero", "name": "edit_Hero", "tokens": ["Webinar - Title"]}],
  "upgrade": {"steps": ["1. Add mktoContainer wrapper...", "2. Convert mktEditable to mktoModule..."]}
}
```

## Upcoming Features

### WCAG Color Contrast Checking
Automated luminance calculation to flag text/background pairs below WCAG AA 4.5:1 ratio. Will add a `--contrast` flag to `lint_email.py` using the WCAG relative luminance formula (`CR = (L1 + 0.05) / (L2 + 0.05)`). No external dependencies needed -- just hex-to-RGB conversion and luminance math. This will catch issues like light gray text on white backgrounds that pass visual inspection but fail for low-vision users.

### CSS AST Parsing
Deeper CSS analysis using the `tinycss2` library to catch issues that regex alone can't reliably detect: nested @-rule problems that trigger Gmail's full style block stripping, invalid shorthand properties that Outlook silently drops, and specificity conflicts between embedded and inline styles. Currently the linter uses regex which handles most cases but misses edge cases in complex `<style>` blocks.

### Outlook Ghost Table Detection
Verify that `max-width` and `inline-block` column layouts have matching MSO conditional comment fallbacks. This requires paired HTML comment parsing (`<!--[if mso]>...<![endif]-->`) alongside DOM analysis to confirm that every hybrid layout column has a corresponding ghost table. Currently the linter flags the symptoms (banned CSS properties) but can't verify the workaround is present.

### Responsive Layout Analysis
Validate hybrid/spongy layout patterns end-to-end: fluid base widths, ghost table pairings, media query progressive enhancement, and source order for mobile stacking. This is architecturally complex because there are many valid responsive email patterns -- the linter needs to understand the *intent* of a layout to validate it, not just flag individual properties.

### v1.0 to v2.0 Auto-Migration
Take a collection of v1.0 email HTMLs, deduplicate shared regions (headers, footers), catalog unique content sections, and generate a v2.0 template skeleton with `mktoContainer`, `mktoModule` wrappers, and `<meta>` variable declarations replacing `{{my.Token}}` references. Currently `detect_version.py` provides the analysis and per-region suggestions; this feature would automate the actual conversion.
