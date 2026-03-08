---
name: mary-email-brief
description: >
  Use this skill whenever a user wants to create a campaign briefing document, brief,
  or token template for a Marketo campaign. Triggers include: "build a briefing doc",
  "create a campaign brief", "briefing for [campaign name]", "token template",
  "fill-in doc", "brief for 3Touch", or any request to generate a structured document
  that maps Marketo program tokens to email/LP content fields.
  Always use this skill when the user mentions building or creating a brief, even if
  they just say "brief me on [campaign]" — if it involves Marketo tokens and campaign
  content, this skill applies.
---

# Mary — Campaign Briefing Document Builder

Mary builds structured DOCX briefing documents for Marketo campaigns. The briefing doc
maps every program token to a labeled, numbered table row that teams fill in — with
pre-populated values where available, visual markers linking rows to email screenshots,
and consistent formatting across all campaign types.

---

## User Request

The user has requested: $ARGUMENTS

Adapt the output based on what the user asked:
- **Campaign name mentioned** (e.g. "briefing for 3Touch") → look up that campaign
  by name and build the brief from its deliverables and tokens
- **"Just Email 1"** or specific deliverable → filter to only that deliverable's tokens
- **"Include screenshots"** → add image placeholder rows before each content table
- **"Quick brief"** or **"just the tokens"** → skip the Instructions Box and image
  placeholders. Output only the numbered content tables with token fields.
- **No specific ask / generic request** → run the full default workflow (all steps)

Always complete Step 0 (campaign identification) and Step 1 (details) regardless of
the request. The adaptation applies to Step 2.

---

## How to Use This Skill

This skill has one reference file. Load it at the right step.

| Reference File | Load When |
|---|---|
| `references/briefing-format.md` | Step 2 — when building the DOCX |

---

## Step 0: Identify the Campaign

Try the MCP tools first. If they're not available, fall back to manual input.

### Path A: MCP Tools Available

1. Extract the campaign name from the user's request
2. Call `allgood_list_campaigns(name="<campaign name>")` to search for the campaign
3. If multiple results, show the list and ask the user to pick one
4. If one result, confirm the match with the user and grab the `targetUri`
5. If no results, broaden the search (shorter name) or ask the user to clarify

### Path B: No MCP Tools

1. Ask the user for the campaign name
2. Ask them to provide the token details via **either**:
   - A screenshot of the Marketo program's My Tokens tab
   - A pasted list of token names and values
3. If they provide a screenshot, read it and extract:
   - Token names (e.g. `{{my.SubjectLine}}`, `{{my.em2-Copy}}`)
   - Current values (if visible)
   - Which emails/deliverables exist
4. If they paste text, parse the token names and any values provided

Do NOT proceed to Step 1 until you have either a `targetUri` (Path A) or a parsed
token list (Path B).

---

## Step 1: Get Campaign Details

### Path A: MCP Tools

1. Call `allgood_get_target_details(target_uri="<targetUri>", include_attributes=true)`
2. From the response, extract:
   - **Campaign name** and description
   - **Deliverables list** — each deliverable's name, description, and targetUri
   - **Attributes** — the `_schema` row tells you column meanings:
     `[value, required, set, validated, description]`
   - For each attribute: note the token name, current value, whether it's required,
     whether it's been set, and its description
3. Determine the **campaign type** from the deliverables:
   - Single email → 1 deliverable
   - Multi-touch email → multiple deliverables named "Email 1", "Email 2", "Email 3"
   - Event + LP → deliverables include an email and a landing page
4. Map tokens to deliverables — tokens with `em2-` prefix belong to Email 2,
   `em3-` prefix to Email 3, unprefixed to Email 1 or shared

### Path B: Manual Input

1. From the screenshot or pasted text, build the same data structure:
   - List of token names → group by email prefix (unprefixed, em2-, em3-)
   - Any values already visible
   - Infer deliverable count from token prefixes
2. Determine campaign type using the same logic as Path A

### For Both Paths

Print a summary for the user before proceeding:
```
Campaign: [name]
Type: [Multi-Touch Email / Event + LP / Single Email]
Deliverables: [list]
Total tokens: [N] ([X] pre-populated, [Y] need input)
```

Ask the user to confirm before building the doc.

---

## Step 2: Build the DOCX Briefing Document

**Read `references/briefing-format.md` now.** Follow the format specification precisely.

Use the `docx` npm library (see DOCX skill for full technical reference).

### Branding (Subtle)

This briefing doc uses lightweight branding — no full cover page.

- **Header (every page):** Small Mary logo (`assets/mary-logo.png`, ~0.5" / 720 DXA
  width) left-aligned. "Campaign Briefing" text right-aligned in pink `#dc4393`, 10pt.
  If logo file is missing, use text "Mary" in pink bold instead.
- **Footer (every page):** Centered allGood logo (`assets/allgood-logo.png`, ~0.4" /
  576 DXA width) with "Powered by allGood" text below in gray `#888888`, 9pt.
  If logo file is missing, use text "Powered by allGood" only.
- **Section headers:** Pink `#dc4393`, Arial 16pt bold — consistent with allGood brand.

### Document Structure

Build the structure based on campaign type:

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
2. **Event Basics** section header
   - Two-column table (Table Type 2) with event tokens (date, time, location, etc.)
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

### Output

Save to `/mnt/user-data/outputs/<campaign-name>-briefing.docx`
(sanitize the campaign name for the filename — lowercase, hyphens, no special chars).

---

## Step 3: Validation Checklist

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
- [ ] Header shows Mary logo (or text fallback) + "Campaign Briefing"
- [ ] Footer shows allGood logo (or text fallback) + "Powered by allGood"
- [ ] Page margins: 1" top/bottom (1440 DXA), 0.75" left/right (1080 DXA)
- [ ] Arial font used throughout
- [ ] Table width is 10,320 DXA (fills page within margins)
- [ ] Token naming follows convention (em2- for Email 2, em3- for Email 3)
- [ ] Campaign type matches the document structure used
- [ ] Cell margins applied: 120 DXA top/bottom, 140 DXA left/right
- [ ] All borders: single, 1pt, `#CCCCCC`
- [ ] Section headers are pink `#dc4393`, 16pt, bold

If any check fails, fix it and re-run the checklist before outputting the file.
