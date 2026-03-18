---
name: mary-email-brief
description: >
  Use this skill whenever a user wants to create a campaign briefing document, brief,
  or token template for a Marketo campaign. Triggers include: "build a briefing doc",
  "create a campaign brief", "briefing for [campaign name]", "token template",
  "fill-in doc", "brief for 3Touch", or any request to generate a structured document
  that maps Marketo program tokens to email/LP content fields.
  Also triggers when the user provides an unstructured document (raw email copy, campaign
  brief, email templates doc) AND an empty briefing template DOCX — and wants the content
  mapped into the structured format. Phrases like "fill in this template", "convert this
  doc", "map this into the brief", "here's the copy and here's the template", or any
  combination of an unstructured doc + a template file should trigger this skill.
  Always use this skill when the user mentions building or creating a brief, even if
  they just say "brief me on [campaign]" — if it involves Marketo tokens and campaign
  content, this skill applies.
---

# Mary — Campaign Briefing Document Builder

Mary builds structured DOCX briefing documents for Marketo campaigns. The briefing doc
maps every program token to a labeled, numbered table row — with pre-populated values,
visual markers linking rows to email screenshots, and consistent formatting across all
campaign types.

---

## User Request

The user has requested: $ARGUMENTS

**First, determine which mode applies:**

- **Document Conversion Mode** — user provides an unstructured doc (raw copy, campaign
  brief, email templates) AND an empty briefing template DOCX → follow the
  Document Conversion workflow below
- **Campaign Build Mode** — user provides a campaign name (with or without MCP access)
  → follow the Campaign Build workflow below

If it's ambiguous, ask: "Do you have an empty briefing template you'd like me to fill,
or should I build the structure from scratch?"

---

## Reference Files

| File | Load When |
|---|---|
| `references/briefing-format.md` | When building or writing any DOCX output |

---

## Document Conversion Mode

Use this when the user provides both an unstructured doc and an empty template DOCX.
The template defines the structure and tokens; the unstructured doc provides the content.

### Step 1: Read the Template

The template is a binary DOCX. Extract its text using Python:

```python
import zipfile
from xml.etree import ElementTree as ET

with zipfile.ZipFile('path/to/template.docx') as z:
    with z.open('word/document.xml') as doc:
        tree = ET.parse(doc)
        ns = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
        for para in tree.iter(ns+'p'):
            parts = [r.text for r in para.iter(ns+'t') if r.text]
            if parts:
                print(''.join(parts))
```

From the extracted text, build a **token inventory** — an ordered list of every token
in the template:

| Row # | Token | Label | Helper Text |
|---|---|---|---|
| 1 | `{{my.em1-SubjectLine}}` | Subject Line | 40-65 characters |
| ... | ... | ... | ... |

Also extract from the Instructions Box:
- **Clone Program** name (pre-filled in template — keep as-is)
- **New Program** field (blank — fill with campaign name from unstructured doc)
- **New Folder**, **Requester Email** (pre-filled — keep as-is)

### Step 2: Read the Unstructured Doc

Extract the text from the unstructured doc the same way (Python zipfile if DOCX, or
read directly if plain text/paste).

Then identify and label every piece of content:

| Content Type | What to look for |
|---|---|
| Campaign name | Document title, heading, or first prominent label |
| Subject line(s) | Lines labeled "Subject:", email subject fields |
| Preheader | Lines labeled "Preheader:", preview text |
| Body copy sections | Paragraphs of email body — may be labeled "Email 1 Body", "Copy", etc. |
| CTA text | Button labels, "Register Now", "Find out more", "CTA:" lines |
| CTA URLs | URLs following or paired with CTA text |
| Images | References to banner images, URLs for image assets |
| Intro/closing text | Introductory or sign-off copy outside the main body |
| Event details | Date, time, location fields |
| Multi-email signals | "Email 1:", "Email 2:", numbered sections, "em2-" / "em3-" references |

For multi-email unstructured docs (e.g. 3 emails in one file), segment the content by
email before mapping. Look for section headings like "Email 1 / Announcement", numbered
groups, or repeated subject-line patterns.

### Step 3: Map Content to Tokens

Work through the token inventory from Step 1 in order. For each token, find the best
matching content from Step 2.

**Matching logic:**

| Token name contains... | Map from unstructured doc... |
|---|---|
| `SubjectLine` | Subject line for that email |
| `Preheader` | Preheader / preview text for that email |
| `Banner-Image` | Banner image URL or asset reference |
| `Intro-Text` | Opening/intro paragraph before the main body sections |
| `Headline` | Main headline inside the email body |
| `Copy`, `Copy1`, `Copy2`... | Body copy sections, in order |
| `CTA1Text`, `CTA2Text`... | CTA button labels, in order |
| `CTA1URL`, `CTA2URL`... | URLs paired with each CTA, in order |
| `copy1-image`, `copy2-image`... | Image URLs paired with each body section |
| `closing-copy` | Closing/sign-off copy at the end of the email |
| `em2-*` | Same logic, but from Email 2 content |
| `em3-*` | Same logic, but from Email 3 content |

**Rules:**
- If a token has a clear match → pre-populate the value cell verbatim from the source
- If a token has no match in the unstructured doc → leave the value cell empty
- Do not invent or paraphrase content — copy it exactly as written
- If the same content could match multiple tokens, prefer the most specific match
  (e.g. a short intro sentence → `Intro-Text`, not `Copy1`)

After mapping, show the user a summary before building:

```
Campaign: [name from unstructured doc]
Template: [template filename]
Tokens mapped: [N] of [total] ([X] pre-populated, [Y] left empty)

Mapped:
  {{my.em1-SubjectLine}} → "Your November insights from Samsara Canada"
  {{my.em1-Copy1}}       → "DATA INSIGHTS\nNew data reveals..."
  ...

Left empty:
  {{my.em1-Banner-Image}}
  ...
```

Ask the user to confirm or correct before building.

### Step 4: Build the DOCX

**Read `references/briefing-format.md` now.** Follow the format specification precisely.

Build the DOCX using the template's structure as the blueprint:
- Replicate the exact section headers, row order, row numbers, and table types from
  the template
- Fill in the value column for each token using the mapping from Step 3
- Fill in "New Program" in the Instructions Box with the campaign name
- Leave all unmapped value cells empty (do not add placeholder text)

Apply all branding, fonts, colors, and layout from `references/briefing-format.md`.
Use the `docx` npm library.

**Branding:**
- **Header (every page):** "Campaign Briefing" left-aligned, pink `#dc4393`, 10pt
- **Footer (every page):** Right-aligned — Mary logo (`assets/mary-logo.png`, 288 DXA)
  + "powered by" gray `#888888` 9pt + allGood logo (`assets/allgood-logo.png`, 432 DXA).
  If logos missing, use text: "Mary powered by allGood" in gray.
- **Section headers:** Pink `#dc4393`, Arial 16pt bold

Save to `/mnt/user-data/outputs/<campaign-name>-briefing.docx`
(sanitize: lowercase, hyphens, no special chars).

### Step 5: Validation

Run the checklist from the Validation Checklist section below before delivering.

---

## Campaign Build Mode

Use this when the user provides a campaign name and wants a briefing built from scratch
(via Marketo MCP or manual token input). No template file is provided.

### Step 0: Identify the Campaign

Try MCP tools first. Fall back to manual input if unavailable.

**Path A: MCP Tools Available**

1. Extract the campaign name from the user's request
2. Call `marketo_get_programs_by_name(name="<campaign name>")` to search
3. If multiple results, show the list and ask the user to pick one
4. If one result, confirm and grab the program `id`
5. If no results, broaden the search or ask the user to clarify

**Path B: No MCP Tools**

1. Ask for the campaign name
2. Ask for token details via a screenshot of the Marketo My Tokens tab or a pasted list
3. Extract: token names (e.g. `{{my.SubjectLine}}`), current values, deliverable names

Do not proceed to Step 1 until you have a program `id` (Path A) or a parsed token list
(Path B).

### Step 1: Get Campaign Details

**Path A: MCP Tools**

1. Call `marketo_get_program_details(programId=<id>)` — extract program name, type,
   channel, and all tokens (name, type, current value)
2. Call `marketo_get_email_details(programId=<id>)` — extract deliverable names,
   subject lines, statuses
3. Determine campaign type: Single Email / Multi-Touch Email / Event + LP
4. Map tokens to deliverables by prefix (`em2-` → Email 2, `em3-` → Email 3,
   unprefixed → Email 1 or shared)

**Path B: Manual Input**

1. Group tokens by email prefix to infer deliverable count
2. Determine campaign type using the same logic

**For both paths**, print a summary and ask the user to confirm:

```
Campaign: [name]
Type: [Multi-Touch Email / Event + LP / Single Email]
Deliverables: [list]
Total tokens: [N] ([X] pre-populated, [Y] need input)
```

### Step 2: Build the DOCX Briefing Document

**Read `references/briefing-format.md` now.** Follow the format specification precisely.

Use the `docx` npm library.

**Branding:**
- **Header (every page):** "Campaign Briefing" left-aligned, pink `#dc4393`, 10pt
- **Footer (every page):** Right-aligned — Mary logo (`assets/mary-logo.png`, 288 DXA)
  + "powered by" gray `#888888` 9pt + allGood logo (`assets/allgood-logo.png`, 432 DXA).
  If logos missing, use text: "Mary powered by allGood" in gray.
- **Section headers:** Pink `#dc4393`, Arial 16pt bold

**Document Structure** — build based on campaign type:

#### Multi-Touch Email Campaigns

1. **Program Details** section header
   - Instructions Box (Table Type 1) — operational instructions for the team
2. **Email 1 Content** section header + italic subtitle (email name/description)
   - Image Placeholder row (Table Type 5) — "[IMAGE PLACEHOLDER: Email 1 Screenshot]"
   - Subject/Preheader table (Table Type 2 — two-column)
   - Content table with header row (Table Type 3 — two-column with dark header)
     OR numbered content table (Table Type 4 — three-column with pink numbers)
3. **Email 2 Content** section header + subtitle
   - Same structure as Email 1, using `em2-` prefixed tokens
4. **Email 3 Content** section header + subtitle (if exists)
   - Same structure, using `em3-` prefixed tokens

#### Event + Landing Page Campaigns

1. **Program Details** section header
   - Instructions Box
2. **Shared Content: Event Details** section header
   - Two-column table (Table Type 2) with event tokens (date, time, location, etc.)
   - Use the "Shared Content:" prefix for any section whose tokens are shared across
     multiple deliverables (e.g. event details used by both emails and landing pages)
3. **Email Content** section header
   - Image Placeholder
   - Content table (Type 3 or Type 4)
4. **Landing Page Content** section header
   - Image Placeholder
   - Three-column numbered table (Table Type 4)

#### Single Email Campaigns

1. **Program Details** section header
   - Instructions Box
2. **Email Content** section header
   - Image Placeholder
   - Subject/Preheader table (Type 2)
   - Numbered content table (Type 4)

### Token-to-Row Mapping

For each token from Step 1, create a table row with the **3-line label structure**:

| Line | Content | Source |
|---|---|---|
| Line 1 | User-friendly name | Map from `references/briefing-format.md` label table |
| Line 2 | Marketo token | The `{{my.TokenName}}` syntax |
| Line 3 | Helper text | From the label table or attribute description |

**Value column:**
- If the token has a value (from allGood or user input) → pre-populate it
- If the token is required but unset → leave empty (the team fills it in)
- If the token is optional and unset → leave empty

### Visual Marker Numbers (3-Column Tables)

When using Table Type 4, assign row numbers following the standard mapping:

| # | Element(s) |
|---|---|
| 1 | Subject Line |
| 2 | Preheader |
| 3 | Banner Image, Banner URL (grouped) |
| 4 | Headline |
| 5 | Greeting, First Name (grouped) |
| 6 | Body Copy |
| 7 | CTA Button Text, CTA URL (grouped) |
| 8 | Secondary Copy |

Grouped fields share the same number and same row background color.

Save to `/mnt/user-data/outputs/<campaign-name>-briefing.docx`
(sanitize: lowercase, hyphens, no special chars).

### Step 3: Validation

Run the checklist below before delivering.

---

## Validation Checklist

After generating the DOCX, verify every item below. Fix any failures before delivering.

- [ ] All tables use the 3-line label structure (friendly name / token / helper text)
- [ ] Line 1 is bold, 11pt, black
- [ ] Line 2 is regular, 9pt, gray `#666666`
- [ ] Line 3 is italic, 8pt, gray `#888888`
- [ ] Pink numbered column (`#dc4393`) has white bold text, centered
- [ ] Grouped fields share the same number (Banner Image + Banner URL = same #)
- [ ] Alternating row backgrounds applied (white / `#efefef`)
- [ ] All required tokens from the campaign are present — none missing
- [ ] Pre-populated values match the source data exactly
- [ ] Empty required fields are clearly empty (not filled with placeholder text)
- [ ] Header shows "Campaign Briefing" left-aligned in pink
- [ ] Footer shows right-aligned single line: Mary logo + "powered by" + allGood logo
- [ ] Page margins: 1" top/bottom (1440 DXA), 0.75" left/right (1080 DXA)
- [ ] Arial font used throughout
- [ ] Table width is 10,320 DXA (fills page within margins)
- [ ] Token naming follows convention (em2- for Email 2, em3- for Email 3)
- [ ] Campaign type matches the document structure used
- [ ] Cell margins applied: 120 DXA top/bottom, 140 DXA left/right
- [ ] All borders: single, 1pt, `#CCCCCC`
- [ ] Section headers are pink `#dc4393`, 16pt, bold

If any check fails, fix it and re-run the checklist before outputting the file.
