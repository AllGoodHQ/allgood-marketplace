# Marketo My Token Editing Reference

> Loaded by `marketo-tokens/SKILL.md` — authoritative reference for token types,
> per-type editing rules, API mechanics, inheritance, and validation.
> Workflows in SKILL.md defer to this file for all correctness decisions.

## Purpose

This reference governs how to read, create, update, and validate Marketo My Tokens via the REST API. Use it whenever editing token values programmatically — the rules differ significantly by token type and getting them wrong causes silent data corruption, broken emails, or lost link tracking.

---

## Token Type Quick-Decision Table

| If the value is… | Use type | API `type` string | Link tracking? |
|---|---|---|---|
| JavaScript, CSS, tracking pixels, raw HTML, URL params, `<img>` tags | **Text** | `text` | No |
| Formatted body content (bold, links, lists, paragraphs) | **Rich Text** | `rich text` | Yes |
| A date (no time component) | **Date** | `date` | N/A |
| An integer or decimal number | **Number** | `number` | N/A |
| A lead score value (supports `+`/`-`/`=` arithmetic) | **Score** | `score` | N/A |

Also exists but rarely edited programmatically: **Calendar File** (`.ics` events, not API-editable via the standard token endpoint — use `create_calendar_token`), **Email Script** (Velocity/VTL, not API-editable), **SFDC Campaign** (Salesforce Campaign ID, API-editable as `sfdc campaign`). These three are mentioned for completeness — the rules below focus on the five primary editable types.

**"Link" and "Image" are not real token types.** There is no standalone Link token or Image token in the My Token system. URLs go in Text tokens (untracked) or Rich Text tokens (tracked via `<a>` tags). Image URLs go in Text tokens and are referenced in template HTML as `<img src="https://{{my.ImageURL}}">`. The UI does show an image token picker, but it cannot be created or updated via the standard Asset Token API.

---

## Type Inference Heuristics (field-name → type)

Apply in order; first match wins:

| Field name contains… | Inferred type | Placeholder value |
|---|---|---|
| `Body`, `Copy`, `Content` | `rich text` | `<p>Edit me.</p>` |
| `Date`, `When` | `date` | `2026-01-01` |
| `Score` | `score` | `0` |
| `Amount`, `Count`, `Number`, `Qty`, `Price` | `number` | `0` |
| `Campaign` (SFDC context) | `sfdc campaign` | `` (empty — user supplies Campaign ID) |
| `Calendar`, `iCal`, `.ics` | calendar (use `create_calendar_token`) | `` |
| `URL`, `Link`, `Image`, `Script`, `HTML`, `Pixel` | `text` | `Edit me.` |
| (anything else) | `text` | `Edit me.` |

Always surface the inferred type in the preview and let the user override per token.

---

## Type 1: Text Token

### Behavior model

Text tokens are **unfiltered pass-through**. Marketo stores the value byte-for-byte and outputs it with zero processing — no HTML sanitization, no JavaScript stripping, no CSS filtering, no entity decoding.

### Size limit

524,288 characters (UTF-8). Note: multibyte characters (emojis, CJK) consume 2–4 bytes each and reduce effective capacity. For ASCII-only content, this is roughly 512 KB.

### What it supports

JavaScript, CSS, `<style>` blocks, tracking codes, URL query strings, raw HTML (rendered by email client, not by Marketo), emojis (use HTML hex entities like `&#x1F600;` for safest cross-client rendering), `<img>` tags, `<script>` tags, CDATA sections, HTML comments, arbitrary whitespace and indentation.

### Link tracking rule

**Links inside Text tokens are NOT tracked.** Clicks will not appear in Marketo reports. This is because Marketo's tracking mechanism scans for the pattern `<a href="http` in raw email HTML *before* token replacement occurs.

**Workaround for tracked links via Text token**: Split the URL — place the protocol in the template HTML and only the path/domain in the token:
```html
<!-- In email template HTML: -->
<a href="https://{{my.URLtoken}}">Click here</a>
```
Marketo sees `<a href="https://` in the raw HTML and applies tracking. The token value should then contain only `example.com/path?param=value` (no protocol).

### Editing rules

1. **Preserve everything exactly.** HTML entities stay encoded (`&lt;` stays `&lt;`, `&amp;` stays `&amp;`). Do not decode them.
2. **Whitespace and indentation are preserved.** Do not reformat, collapse, or normalize whitespace.
3. **Apply user changes literally.** If the user provides content with specific formatting, spacing, or escaping, keep it.
4. **Line break behavior is inconsistent.** The UI presents a single-line text input. Line breaks can be inserted via API. In batch campaigns, newline characters (`\n`) are replaced with spaces. In trigger campaigns, newlines are preserved. If the user needs visible line breaks in email output, they must use `<br>` tags explicitly.
5. **If user adds a link**: Warn that clicks will not be tracked in Marketo reports unless the protocol is split into the template HTML.
6. **If user adds line breaks without `<br>`**: Note that they need `<br>` tags for visible line breaks in emails, and that `\n` behavior differs between batch and trigger campaigns.
7. **Spaces in token names break URLs.** If a token value will appear in a URL context (query params, `href`, `src`), the token name must not contain spaces — Marketo renders them as `%20`, breaking the URL. Use hyphens or camelCase for token names.

---

## Type 2: Rich Text Token

### Behavior model

Rich Text tokens are **filtered HTML**. Marketo processes the content through its Rich Text Editor (RTE) engine, which sanitizes HTML, enables link tracking, and strips unsupported elements. The value you set via API may not be identical to what Marketo stores — the RTE modifies it.

### Size limit

Not officially documented. There is no published size limit for Rich Text tokens (unlike Text tokens at 524,288 characters). In practice, keep values reasonable for email content.

### What it supports

`<p>`, `<strong>`/`<b>`, `<em>`/`<i>`, `<u>`, `<a>` (with automatic link tracking), `<img>`, `<span>` (with inline styles), `<br>`, `<div>`, `<h1>`–`<h6>`, `<ul>`/`<ol>`/`<li>`, font family/size/color via inline styles, text alignment, indentation.

### What it strips or breaks

- **JavaScript** — All `<script>` tags and inline JS are stripped silently.
- **CDATA sections** — Stripped.
- **`<style>` blocks** — Stripped. Use inline styles only.
- **CSS classes** — May be stripped or auto-converted to inline styles. Do not rely on class-based styling.
- **`<video>` tags** — Stripped.
- **Nested tokens `{{my.token}}`** — Rendered as literal text, not resolved. Token nesting does not work in Rich Text (or any standard My Token type). Only Email Script (Velocity) tokens can reference other tokens.
- **`<code>` tags** — Not reliably supported. Convert to `<span style="font-family: monospace;">`.
- **HTML comments** — May be disrupted by paragraph filtering.

### Link tracking rule

**Links in Rich Text tokens ARE tracked.** Marketo automatically wraps `<a href>` links with tracking redirects. Every link must start with `https://` or `http://` — relative URLs and protocol-relative URLs are not supported.

### Critical gotchas

**Zero-width space injection**: Marketo's RTE silently inserts zero-width space characters (U+200B, `&#8203;`) between `</p>` and `<p>` tags. These invisible characters break functionality if the rich text content is consumed in a JavaScript context, displayed in preheader text, or compared string-for-string. Always strip U+200B and other invisible Unicode (U+FEFF, U+200C, U+200D) when reading Rich Text values.

**Single-paragraph tag stripping**: When a Rich Text token contains only a single paragraph of text, Marketo automatically strips the surrounding `<p>` tags when rendering in an email. Multi-paragraph content retains `<p>` wrapping. This inconsistency can cause unexpected layout shifts.

**Root element is always `<p>`**: Rich Text program tokens always use `<p>` as the root block element. This cannot be changed to `<div>` or none (unlike the email editor which offers that option).

**Paragraph tag auto-insertion**: The RTE automatically wraps bare text in `<p>` tags and may insert additional `<p>` tags around content. If you need precise control over paragraph structure, account for this.

### Editing rules

1. **Unescape HTML entities first** when reading existing values for editing. The API returns entity-encoded content; decode `&lt;` → `<`, `&amp;` → `&`, etc. before processing. Re-encode only if needed for the specific output context.
2. **Strip `<mark>` tags** (keep inner text). These are highlighting artifacts from the UI editor.
3. **Remove `<blockquote>` inside `<li>`**. The RTE sometimes nests blockquotes inside list items incorrectly.
4. **Convert `<code>` to `<span style="font-family: monospace;">`** since `<code>` tags are not reliably rendered.
5. **Strip zero-width and invisible Unicode**: Remove U+200B (zero-width space), U+FEFF (BOM), U+200C (zero-width non-joiner), U+200D (zero-width joiner) from content.
6. **Links must include inline color style.** A bare `<a href="https://example.com">text</a>` may lose its color. Always include: `<a href="https://example.com" style="color: #0000FF;">text</a>` (or the appropriate brand color).
7. **Links must use absolute URLs** starting with `https://` or `http://`.
8. **CSS classes are unreliable.** Any class-based styling should be converted to inline styles before saving.
9. **Images in `<img>` tags and `background-image` declarations** may be auto-uploaded by Marketo's internal content preparation system and rewritten to CDN URLs.

---

## Type 3: Date Token

### Behavior model

Date tokens store date-only values (no time component). The API accepts and returns dates in ISO format.

### Input handling

- API input/output format: `yyyy-MM-dd` (e.g., `2026-04-15`)
- UI input format: `MM/DD/YYYY` (US locale)
- If input format is ambiguous (e.g., `04-06-2026` — is that April 6 or June 4?), assume US convention: `MM-dd-yyyy`

### Output rule

Always output as `yyyy-MM-dd`. This is the only format the API accepts.

### Datetime workaround

There is no native datetime token type. To store a datetime value (e.g., for Advanced Wait steps), use a **Text token** with the format `yyyy-MM-dd HH:mm:ss` (space-separated). The time component is interpreted in the Marketo instance's local timezone. This is an undocumented but widely-used technique.

---

## Type 4: Number Token

### Behavior model

Stores integer or floating-point numeric values. No arithmetic operations — purely a value container.

### Constraints

- UI enforces a maximum of **99,999,999** and does not allow negative values
- The API documentation says "an integer or floating point number" without those UI restrictions — a known inconsistency
- For safety, stay within the UI range unless you have confirmed API-only usage

---

## Type 5: Score Token

### Behavior model

Stores a signed 32-bit integer designed for lead scoring workflows. This is the only token type that supports arithmetic operations.

### Range

-2,147,483,648 to +2,147,483,647 (signed 32-bit integer)

### Operators

Supports `=` (set), `+` (increment), `-` (decrement) via the "Change Score" flow step.

### Difference from Number

Score is specifically designed for lead scoring — it supports arithmetic in flow steps and is the correct choice when the value will be modified by campaigns. Number is a static value container.

---

## API Mechanics

### Endpoint

All token CRUD operations use:
```
POST /rest/asset/v1/folder/{folderId}/tokens.json
GET  /rest/asset/v1/folder/{folderId}/tokens.json
```

### Encoding — critical

The API uses **`application/x-www-form-urlencoded` encoding, NOT JSON.** This is the most common integration mistake. The request body must be form-encoded.

### Required parameters (create/update)

| Parameter | Rules |
|---|---|
| `name` | Max **50 characters**. Avoid spaces if value will appear in URLs. |
| `type` | Exact string: `text`, `rich text`, `date`, `number`, `score`, `sfdc campaign` |
| `value` | The token content. For Rich Text, this is HTML. |
| `folderType` | Either `"Folder"` or `"Program"`. Defaults to `"Folder"` if omitted — does NOT search both. This is a common source of "token not found" errors. |

### Upsert behavior

The create endpoint is an **upsert**: if a token with the same name and type exists on that folder/program, it updates the value. If not, it creates a new token.

### Authentication

Use the `Authorization: Bearer {access_token}` header. Community reports indicate the query parameter approach (`?access_token=xxx`) intermittently returns error 600.

### Rate limits

- 100 calls per 20 seconds
- 50,000 calls per day
- Maximum 10 concurrent calls
- No bulk token API — each token requires a separate POST

### Body size

API body limit is **1 MB**. URI length capped at **8 KB**. Always pass large Rich Text values in the POST body, never as URL query parameters.

### GET returns only local tokens

The GET endpoint returns tokens **directly defined** on the specified folder/program. It does NOT return inherited tokens. To discover the full token landscape, you must walk the folder tree upward.

---

## Token Inheritance

### How it works

Tokens inherit downward through Marketo's folder hierarchy. A token set on a parent folder is available to all child folders and programs beneath it.

### Resolution order (runtime)

Local program tokens → parent folder tokens (walking up) → system tokens → default values. The most specific (closest to the asset) value wins.

### Critical limitation: overridden tokens cannot be re-inherited

Once you override an inherited token at a child level, updates to the parent token no longer flow down — even if you delete the local override. This is a permanent break in inheritance. The only workaround is to rename the local token (the inherited version then reappears), but this fails if the token is already referenced in assets.

### Engagement program gotcha

If an email lives inside a default program that is a child of an engagement program, tokens resolve from the **default program** — not the engagement program doing the sending. This catches people off guard when tokens seem to "not work" in nurture streams.

---

## My Tokens vs. Email 2.0 Template Variables — Don't Confuse Them

These are two separate systems that coexist in Marketo emails:

| Aspect | My Tokens | Template Variables |
|---|---|---|
| Syntax | `{{my.TokenName}}` | `${variableName}` |
| Defined in | Program/folder token tab | `<meta>` tags in template `<head>` |
| Scope | Inherited through folder tree | Local to the email instance |
| Edited via | API Asset Token endpoints, UI token tab | Email editor sidebar, `fullContent` API |
| Types | text, rich text, date, number, score, etc. | mktoString, mktoNumber, mktoColor, mktoBoolean, mktoList, mktoHTML, mktoImg |

My Tokens can be placed inside Email 2.0 editable elements (`mktoText`, `mktoImg`, etc.). Template variables are declared in the template and configured per-email.

**Marketo email syntax (`mktoModule`, `mktoContainer`, `mktoText`) does NOT work inside Rich Text tokens or Snippets** — it only works in templates and individual emails.

---

## Common Editing Scenarios — Decision Guide

**User wants to add a tracked link:**
→ Use Rich Text token with `<a href="https://..." style="color: #XXXX;">link text</a>`. Or use a Text token with the protocol split into the template HTML.

**User wants to embed JavaScript (tracking pixel, analytics):**
→ Must use Text token. Rich Text will strip all `<script>` tags silently.

**User wants to insert an image:**
→ Store the image URL in a Text token. Reference it in the template as `<img src="https://{{my.ImageURL}}">`. Ensure the token name has no spaces.

**User wants formatted body content (bold, lists, colors):**
→ Use Rich Text token. Apply all styling inline, not via classes.

**User wants to store a URL for use in `href`:**
→ Text token. If tracking is needed, the protocol (`https://`) must be in the template HTML, not in the token value.

**User wants a date for wait steps or event dates:**
→ Date token for date-only (`yyyy-MM-dd`). Text token with `yyyy-MM-dd HH:mm:ss` for datetime.

**User wants to reference a token inside another token:**
→ Not possible with standard My Tokens. Only Email Script (Velocity) tokens can reference other tokens. Rich Text tokens render `{{my.other}}` as literal text.

---

## Validation Checklist — Run Before Saving

For **all token types**:
- [ ] Token name ≤ 50 characters
- [ ] Token name has no spaces if value appears in URL contexts
- [ ] `folderType` parameter matches actual container (`"Folder"` vs `"Program"`)
- [ ] `type` string is exact match (e.g., `rich text` not `richtext` or `Rich Text`)

For **Text tokens**:
- [ ] HTML entities preserved as-is (not decoded)
- [ ] Whitespace/indentation preserved exactly
- [ ] Value ≤ 524,288 characters
- [ ] If contains links: user informed that clicks won't be tracked
- [ ] If contains `\n` line breaks: user informed about batch vs trigger inconsistency; suggest `<br>` tags

For **Rich Text tokens**:
- [ ] Zero-width Unicode stripped (U+200B, U+FEFF, U+200C, U+200D)
- [ ] `<mark>` tags stripped (inner text kept)
- [ ] `<blockquote>` removed from inside `<li>`
- [ ] `<code>` converted to `<span style="font-family: monospace;">`
- [ ] All links use absolute URLs (`https://` or `http://`)
- [ ] All links include inline `style="color: #XXXX;"` attribute
- [ ] No `<script>`, `<style>`, or `<video>` tags (will be stripped silently)
- [ ] No `{{my.token}}` references (will render as literal text)
- [ ] No CSS classes relied upon for critical styling (convert to inline)

For **Date tokens**:
- [ ] Output format is `yyyy-MM-dd`
- [ ] Ambiguous input interpreted as US `MM-dd-yyyy`

For **Number tokens**:
- [ ] Value within range (0 to 99,999,999 for UI compatibility)
- [ ] Valid integer or float

For **Score tokens**:
- [ ] Value within signed 32-bit range (-2,147,483,648 to +2,147,483,647)
- [ ] Valid integer (no floats)
