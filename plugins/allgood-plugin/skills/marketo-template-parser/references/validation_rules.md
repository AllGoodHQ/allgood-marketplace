# Marketo Email 2.0 Template Validation Rules

> **Scope:** These rules cover Marketo Email 2.0 structural validation (`validate.py`). For email HTML rendering best practices across Outlook, Gmail, Apple Mail, dark mode, and accessibility, see `email-rendering-rules.md` and use `lint_email.py`.

## Critical Errors (Template Will Fail)

### Container Rules
1. **Exactly ONE `mktoContainer` per template**
   - Zero containers → Template not modular
   - Multiple containers → "Invalid Module" error
   - Check: `soup.find_all(class_=re.compile("mktoContainer"))`
   - Expected: Length = 1

2. **Containers can ONLY contain Modules as direct children**
   - No other HTML elements allowed (no `<br>`, comments, or wrapper `<div>` tags)
   - Only `mktoModule` elements can be direct children
   - Stray elements trigger "Invalid Module" error

3. **Modules cannot be nested inside other modules**
   - Each module must be a direct child of the container
   - Check: No `mktoModule` inside another `mktoModule`

### ID Rules
4. **All `id` values must be unique across entire template**
   - Check: Build set of all IDs from modules, variables, and editable elements
   - Detect duplicates
   - Consequence: Editor crash, random ID suffixes appended, broken CSS references

5. **ID format constraints**
   - Allowed: Letters (a-z, A-Z), numbers (0-9), dash (-), underscore (_)
   - Not allowed: Spaces, periods, special characters
   - Pattern: `^[a-zA-Z0-9_-]+$`

### Element Pairing Rules
6. **Module element type must match container element type**
   - If container is `<table>` → modules must be `<tr>`
   - If container is `<tbody>`, `<thead>`, `<tfoot>` → modules must be `<tr>`
   - If container is `<td>` → modules must be `<table>`

### Required Attributes
7. **All modules require: `class`, `id`, `mktoName`**
8. **All mktoText elements require: `class`, `id`, `mktoName`**
9. **All mktoImg elements require: `class`, `id`, `mktoName`**
10. **All mktoSnippet elements require: `class`, `id`, `mktoName`**
11. **All mktoVideo elements require: `class`, `id`, `mktoName`**
12. **Container requires: `class`, `id`**

### Token Resolution Rules
13. **Unresolved tokens in HTML attributes outside editable regions**
    - `{{my.*}}`, `{{lead.*}}`, `{{company.*}}` in attribute values (href, src, style, etc.) that are NOT inside a `mktoText` ancestor will NOT resolve via Marketo's fullContent API
    - The literal token string (e.g. `{{my.Speaker1-URL}}`) appears in the sent email
    - `{{system.*}}` tokens (e.g. `{{system.unsubscribeLink}}`) are excluded — they resolve at send-time regardless
    - Fix Option A: Declare an `mktoString` variable in `<head>` and use `${variableId}` in the attribute
    - Fix Option B: Wrap the element in a `mktoText` div so the entire block is editable
    - Check: Regex scan body attributes for `{{(my|lead|company)\.[^}]+}}`, skip elements with `mktoText` ancestry
    - See `references/variable-naming-conventions.md` for full details and examples

---

## Non-Critical Warnings (Best Practices)

### Case Sensitivity
13. **Class names are CASE-SENSITIVE**
    - `mktoText` works, `mktotext` does NOT
    - `mktoModule` works, `mktomodule` does NOT
    - Element silently ignored by parser if wrong case
    - Common errors: `mktotext`, `mktoimg`, `mktomodule`

14. **Custom attribute names are NOT case-sensitive (but camelCase recommended)**
    - `mktoName` = `mktoname` (both work)
    - `mktoModuleScope` = `mktomodulescope` (both work)
    - Recommendation: Use camelCase (`mktoName`, `mktoModuleScope`) for consistency
    - Check for lowercase variants: `mktoname`, `mktomodulescope`, `mktoimglink`, etc.

### Variable Declaration Issues
15. **Unused variables**
    - Variable declared in `<head>` but never referenced in body
    - Check: Find all `${variableID}` references, compare to declared variables
    - Warning only (doesn't break template)

16. **Missing default values**
    - Variables without `default` attribute
    - May cause empty content in preview mode
    - Check: `<meta>` tags missing `default` attribute

### Variable Naming
17. **Variable naming conventions (camelCase preferred)**
    - Variable IDs should use camelCase (e.g. `ctaUrl` not `cta_url` or `cta-url`)
    - Structure: `[context][Descriptor]` (e.g. `speaker1Url`, `heroBackgroundColor`)
    - Match sibling `mktoText` element ID prefixes for consistency
    - Check: Regex `[_-][a-zA-Z]` on variable IDs
    - See `references/variable-naming-conventions.md` for full guide

18. **URL variable defaults missing protocol**
    - `mktoString` variables whose ID or name contains "url", "link", or "href" should have defaults starting with `https://`
    - Missing protocol can cause double-protocol bugs (e.g. `https://https://example.com`)
    - Check: Non-empty defaults on URL-like variables that don't start with `http://` or `https://`

---

## Validation Script Output Format

```json
{
  "valid": true|false,
  "score": 0-100,
  "errors": [
    {
      "type": "duplicate_id|missing_container|nested_modules|invalid_id_format|missing_attribute|unresolved_token_in_attribute",
      "message": "Human-readable error message",
      "line": 123,
      "element": "heroModule"
    }
  ],
  "warnings": [
    {
      "type": "case_sensitivity|unused_variable|missing_default|naming_convention|url_missing_protocol",
      "message": "Human-readable warning message",
      "line": 456,
      "element": "global_preheader"
    }
  ],
  "stats": {
    "modules": 30,
    "variables": 75,
    "unique_ids": 341,
    "editable_elements": 89,
    "containers": 1
  }
}
```

## Score Calculation
- Start at 100
- Subtract 10 points per error
- Subtract 1 point per warning
- Clamped to 0–100
- Valid if errors.length === 0 (warnings affect score but not validity)
