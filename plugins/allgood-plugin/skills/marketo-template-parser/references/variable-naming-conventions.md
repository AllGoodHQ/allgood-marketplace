# Marketo Email 2.0 — Variable ID Naming Conventions

## Overview

Marketo does not enforce a naming convention beyond technical validity rules. However, community consensus and API usage patterns have established clear best practices.

---

## Technical Rules (Enforced by Marketo)

| Rule | Detail |
|------|--------|
| Allowed characters | Letters (`a-z`, `A-Z`), numbers (`0-9`), dash (`-`), underscore (`_`) |
| No spaces | Spaces are not allowed |
| Must be unique | Across the entire template — all elements, modules, variables, and containers |

Violations cause validation failure or silent breakage.

---

## Naming Convention Best Practices (Community Standard)

### 1. Use camelCase

The dominant convention is camelCase for variable `id` values.

```html
<!-- ✅ CORRECT -->
<meta class="mktoString" id="speaker1Url" mktoName="Speaker 1 URL" default="https://">
<meta class="mktoColor" id="buttonColor" mktoName="Button Color" default="#6837ef">

<!-- ❌ AVOID -->
<meta class="mktoString" id="url1" mktoName="Speaker 1 URL" default="https://">
<meta class="mktoColor" id="color1" mktoName="Button Color" default="#6837ef">
```

### 2. Structure as `[context][Descriptor]`

Prefix with the module or element context so variables are grouped and scannable.

```
speaker1Url       → speaker module 1, URL field
speaker1Cta       → speaker module 1, CTA label
speaker2Url       → speaker module 2, URL field
heroBackgroundColor → hero module, background color
buttonBorderRadius  → button, border radius
```

### 3. Match sibling element IDs

If a module already has `mktoText` elements with IDs like `speaker1Copy` and `speaker1Cta`, variable IDs should follow the same prefix pattern:

```html
<!-- Element IDs in the module -->
<div class="mktoText" id="speaker1Copy" mktoname="Speaker 1 Copy">...</div>
<div class="mktoText" id="speaker1Cta" mktoname="Speaker 1 CTA">...</div>

<!-- Variable IDs should match the same prefix -->
<meta class="mktoString" id="speaker1Url" mktoName="Speaker 1 URL" default="https://">
```

### 4. `id` is developer/API-facing; `mktoName` is user-facing

The `id` is used when referencing variables via the Marketo API and in `${variableId}` template references. The `mktoName` is what the end user sees in the email editor. Keep `id` concise and consistent; make `mktoName` fully descriptive.

```html
<meta class="mktoString" id="speaker1Url" mktoName="Speaker 1 URL" default="https://">
```

- `id="speaker1Url"` → used in `href="${speaker1Url}"` and API calls
- `mktoName="Speaker 1 URL"` → shown as the label in the Marketo email editor UI

---

## URL Variable Special Rules

When using `mktoString` for URLs (e.g., in `href` attributes), always include the full protocol in the `default` value:

```html
<!-- ✅ CORRECT: protocol in default -->
<meta class="mktoString" id="speaker1Url" mktoName="Speaker 1 URL" default="https://">
<a href="${speaker1Url}">Learn More</a>

<!-- ❌ INCORRECT: protocol hardcoded in href -->
<meta class="mktoString" id="speaker1Url" mktoName="Speaker 1 URL" default="example.com/page">
<a href="https://${speaker1Url}">Learn More</a>
<!-- Breaks if user enters a full URL → produces "https://https://example.com" -->
```

---

## Why `{{my.token}}` in Attributes Won't Resolve

`{{my.token}}` references placed directly in HTML attributes (e.g., `href="{{my.Speaker1-URL}}"`) are **not wrapped in an editable region** and will not resolve in the `fullContent` API response.

The `fullContent` API reflects the editor-resolved content of `mktoText` editable divs. Tokens sitting in an `href` attribute are outside that resolution scope.

**This works** (token inside mktoText):
```html
<div class="mktoText" mktoname="Speaker 1 Copy" id="speaker1Copy">
  {{my.Speaker1-Copy}}
</div>
```

**This does NOT work** (token naked in attribute):
```html
<a href="{{my.Speaker1-URL}}" ...>Click here</a>
```

### Fix Options

**Option A — `mktoString` variable (preferred for independent URL editing)**
```html
<meta class="mktoString" id="speaker1Url" mktoName="Speaker 1 URL" default="https://">
<a href="${speaker1Url}">CTA Text</a>
```

**Option B — Wrap the anchor in a `mktoText` div**
```html
<div class="mktoText" id="speaker1Cta" mktoname="Speaker 1 CTA">
  <a href="{{my.Speaker1-URL}}">{{my.Speaker1-CTA}}</a>
</div>
```

Option A is preferred when the URL needs to be independently editable or API-settable. Option B is simpler when the entire CTA block (link + label) is edited together.

---

## Summary Table

| Aspect | Recommendation |
|--------|---------------|
| Case style | camelCase |
| Structure | `[context][Descriptor]` |
| Consistency | Match sibling `mktoText` element ID prefixes |
| `id` purpose | Developer/API reference; keep concise |
| `mktoName` purpose | Editor UI label; make fully descriptive |
| URL defaults | Always include `https://` in the default value |
| Token in `href` | Will NOT resolve in `fullContent` — use `${variableId}` instead |
