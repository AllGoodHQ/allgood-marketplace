# Marketo My Token — Naming & Numbering Conventions

> Loaded by `marketo-tokens/SKILL.md` during Workflow A (create from Google Doc)
> when detecting the doc's token convention and, if needed, converting old names
> to the standard format. For type rules and validation, see `token-editing-rules.md`.

---

## The Standard Format

All My Tokens follow this structure:

```
NNN Label - Field Name
```

| Part | Description | Example |
|---|---|---|
| `NNN` | 3-digit number scoping the token to its section | `104` |
| `Label` | Section name from the doc (e.g. "Invite 1", "TYFA") | `Invite 1` |
| `Field Name` | Human-readable field description | `Body Copy` |

Full example: `104 Invite 1 - Body Copy` → referenced in Marketo as `{{my.104 Invite 1 - Body Copy}}`.

---

## Numbering Blocks

Tokens are grouped into hundreds blocks by section.

| Block | Scope |
|---|---|
| 001–099 | Shared / global tokens that don't belong to any single email |
| 100–199 | First section (e.g. Invite 1) |
| 200–299 | Second section (e.g. Invite 2) |
| 300–399 | Third section (e.g. Invite 3) |
| 400–499 | Fourth section |
| 500–599 | Fifth section (e.g. TYFA) |
| 600–699 | Sixth section (e.g. SWMY) |
| …etc. | Each additional section gets the next hundreds block |

### Canonical numbering rule

**Within each block, tokens are numbered sequentially in the order they appear in the doc, starting at X00.**

So a section that only has a Subject Line and Body Copy gets `100` and `101` — not `100` and `105`. The field-name lookup table below is a *suggestion for the field-name portion*, not a fixed number assignment.

**Example sequence for a 3-email program with shared tokens:**

```
001 Webinar Reg URL           ← shared
100 Invite 1 - Subject Line
101 Invite 1 - Banner Image
102 Invite 1 - Preheader
103 Invite 1 - Headline
104 Invite 1 - Body Copy
105 Invite 1 - CTA
106 Invite 1 - UTM
200 Invite 2 - Subject Line
201 Invite 2 - Banner Image
...
300 Invite 3 - Subject Line
...
```

---

## Detecting Sections in a Doc

Section headings in the Google Doc define the numbering blocks. Look for:
- Headings like "Email 1 Content", "Invite 2", "TYFA", "SWMY"
- Table section labels
- `em2-` or `em3-` prefixes on old-style tokens — each unique prefix = one section

Tokens before the first section heading, or explicitly labeled as shared (e.g. "Shared Tokens", "Global"), go into the 001–099 block.

**No section heading but tokens are clearly scoped by `em{n}-` prefix:** derive the label from the token group (e.g. `em2-Copy`, `em2-SubjectLine` → label is "Email 2" or, if the doc has a cover sheet mentioning the email's purpose, use that). If no better label is available, default to `Email N` where N matches the `em` prefix.

---

## Converting Old-Style Names to New Format

Some docs still use the old camelCase or `em{n}-` prefix convention. Convert these when encountered.

### Step 1 — Group into sections

- Old `em{n}-` prefix → `{n}`-th hundreds block (`em1-` → 100s, `em2-` → 200s, …)
- Old camelCase without prefix → treat as Email 1 (100s block) unless the doc clearly indicates otherwise
- Tokens declared as shared/global → 001–099 block

### Step 2 — Assign numbers sequentially within each block

Order tokens by their appearance in the doc, starting at X00.

### Step 3 — Translate the field name

Use the field-name lookup below to produce the human-readable field portion. This table is a *field-name translation only* — it does **not** dictate the number.

| Old name | Field name |
|---|---|
| `SubjectLine` | `Subject Line` |
| `Preheader` | `Preheader` |
| `Banner` | `Banner Image` |
| `BannerURL` | `Banner URL` |
| `Headline` | `Headline` |
| `Greeting` | `Greeting` |
| `Copy` | `Body Copy` |
| `Copy2` | `Secondary Copy` |
| `CTA1Text` | `CTA` |
| `CTA1URL` | `CTA URL` |
| `ImageBottom` | `Image Bottom` |
| `CTA2Text` | `CTA 2` |
| `CTA2URL` | `CTA 2 URL` |

For `em{n}-` prefixed names, strip the prefix before looking up the field name.

### Step 4 — Build the final name

Combine `NNN` + section label + ` - ` + field name.

**Example** (3-email program, doc ordered Subject → Copy for each email):

| Old name | Section | Position | New name |
|---|---|---|---|
| `SubjectLine` | Email 1 | 1st | `100 Email 1 - Subject Line` |
| `Copy` | Email 1 | 2nd | `101 Email 1 - Body Copy` |
| `em2-SubjectLine` | Email 2 | 1st | `200 Email 2 - Subject Line` |
| `em2-Copy` | Email 2 | 2nd | `201 Email 2 - Body Copy` |

Before executing, show the conversion mapping to the user and ask for confirmation.

---

## 50-Character Limit

Marketo enforces a 50-character maximum on token names. Flag any name that would exceed this after conversion. Suggested fix: shorten the field name portion (the `NNN` and label are usually load-bearing for identification).

```
Too long:  500 TYFA - Very Long Descriptive Field Name Here  (52 chars)
Fixed:     500 TYFA - Long Descriptive Field Name            (46 chars)
```

Auto-shorten heuristic: drop trailing adjectives, collapse "the/a/an", abbreviate common words (`Description` → `Desc`, `Information` → `Info`). Always show the shortened form for user approval — never silently rename.

---

## Spaces in Token Names — URL Context Warning

If the token value will be rendered inside a URL (query parameter, `href`, `src`), the token **name** must not contain spaces — Marketo renders them as `%20`, which can break the URL.

Since the standard format `NNN Label - Field Name` contains spaces, tokens destined for URL contexts should either:
- Use an alternate name without spaces (hyphen-separated or camelCase), or
- Live in template HTML where the URL is constructed with the protocol outside the token (see the Text token "workaround for tracked links" in `token-editing-rules.md`).

---

## Tokens to Skip

Don't create these — they are Marketo system tokens, not My Tokens:

- `{{lead.*}}` — e.g. `{{lead.FirstName}}`
- `{{system.*}}`
- `{{company.*}}`
- `{{program.*}}`, `{{campaign.*}}`, `{{member.*}}` — program/campaign/member context tokens

Only create tokens that use `{{my.*}}`.
