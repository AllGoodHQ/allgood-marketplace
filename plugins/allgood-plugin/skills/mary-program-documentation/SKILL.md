---
name: mary-program-documentation
description: >
  Use this skill whenever a user wants to document a Marketo program, create a
  program one-pager, generate program documentation, or audit a program's setup.
  Triggers include: "document this program", "program one-pager", "program
  documentation for [name]", "audit this program", "what's in this program",
  "summarize program [name]", "program overview doc", or any request to produce
  a structured DOCX describing a Marketo program's configuration, assets, tokens,
  smart campaign logic, and health status.
  Always use this skill when the user mentions documenting, auditing, or summarizing
  a Marketo program — if it involves pulling program details and producing a
  structured document, this skill applies. Even casual requests like "tell me
  everything about program X" or "give me a doc on this program" should trigger it.
---

# Mary — Marketo Program Documentation Builder

Mary builds structured DOCX documentation for Marketo programs. Given a program name,
she pulls all available data via MCP — metadata, tokens, smart campaigns (including
flow steps and smart list criteria), emails, forms, landing pages — then analyzes
health flags and produces a branded one-pager covering everything ops needs to know.

---

## User Request

The user has requested: $ARGUMENTS

---

## Reference Files

| File | Load When |
|---|---|
| `references/api-field-mapping.md` | Step 2 — when pulling and mapping MCP data |
| `references/health-checks.md` | Step 3 — when analyzing red flags |
| `references/document-format.md` | Step 4 — when building the DOCX |

---

## Step 1: Identify the Program

Extract the program name from the user's request. Then find it in Marketo.

1. Call `marketo_get_programs_by_name(name="<program name>")`
2. If **multiple results**: show the list (name, type, channel, folder) and ask the
   user to pick one
3. If **one result**: confirm with the user — "I found [name] ([type], [channel]).
   Is this the right program?"
4. If **no results**: try a broader search term, or fall back to
   `get_program_by_name(name="<name>")` (direct Marketo MCP, exact match). If still
   nothing, ask the user to double-check the name.

**Gate:** Do NOT proceed to Step 2 until you have a confirmed program ID.

---

## Step 2: Pull All Program Data

**Read `references/api-field-mapping.md` now** for the full tool chain and field mapping.

Two tool sets are available — allGood wrappers (convenient for search/tokens) and direct
Marketo MCP (required for smart campaigns, flow steps, smart list criteria, forms).
Use both as needed.

### 2a. Program metadata

```
get_program_by_id(id=<programId>)
```

This returns: name, type, channel, description, status, folder, workspace, tags, costs,
SFDC sync info, created/updated dates.

If the allGood wrapper was used in Step 1 and already returned full details, you can
skip this call and use that data instead.

### 2b. My Tokens

```
get_tokens_by_folder(id=<programId>, folderType="Program")
```

Returns all local tokens (name, type, value). Inherited tokens are NOT included —
note this in the document.

### 2c. Smart Campaigns

```
browse_smart_campaigns(folder={id: <programId>, type: "Program"})
```

This lists all smart campaigns in the program. For **each** smart campaign returned:

```
get_smart_campaign_by_id(id=<campaignId>, includeFlowSteps=true)
```

This returns the campaign metadata AND its flow steps — the actions it performs, in
order, including choice steps and wait steps. This is the most valuable data for
documentation because flow steps define what the program actually *does*.

Then get the smart list (triggers + filters) for each campaign:

```
get_smart_list_by_campaign_id(smartCampaignId=<campaignId>, includeRules=true)
```

Returns the full filter/trigger criteria with operators, values, and AND/OR logic.

For batch campaigns, also check for scheduled runs:

```
get_smart_campaign_scheduled_runs(campaignId=<campaignId>)
```

### 2d. Emails

```
browse_emails2(folder={id: <programId>, type: "Program"})
```

Lists all emails. For each email:

```
get_email_content(id=<emailId>)
```

Returns subject line, from name/address, reply-to, content sections, status, and
operational flag.

### 2e. Forms

Use `get_folder_content(id=<programId>)` to find forms, then for each:

```
get_form_by_id(id=<formId>)
get_form_fields(id=<formId>)
```

Returns form metadata and all fields (name, dataType, required, validation rules,
progressive profiling settings).

### 2f. Lists

```
browse_smart_lists(folder={id: <programId>, type: "Program"})
browse_lists(folder={id: <programId>, type: "Program"})
```

Returns smart lists and static lists within the program.

### 2g. Landing Pages and other assets

Use `get_folder_content(id=<programId>)` to discover any landing pages, reports, or
other assets not covered above. Document their names, types, and statuses.

### Rate limit awareness

Marketo enforces 100 API calls per 20 seconds and 50,000 calls per day. For programs
with many smart campaigns (10+), pace your detail calls. If you hit rate limits, wait
20 seconds and retry.

### Summary and confirmation

After pulling all data, print a summary for the user:

```
Program: [name]
Type: [type] | Channel: [channel] | Status: [status]

Assets found:
  Smart Campaigns: [N] ([X] active, [Y] inactive)
  Emails: [N]
  Landing Pages: [N]
  Forms: [N]
  Smart Lists: [N] | Static Lists: [N]

Tokens: [N] local tokens ([X] populated, [Y] empty/placeholder)

Red flags detected: [N] (will be detailed in the document)

Ready to build the documentation. Proceed?
```

Wait for user confirmation before building.

---

## Step 3: Analyze Health Flags

**Read `references/health-checks.md` now** for the full rule set and detection logic.

Run every health check rule against the collected data. Each rule has an ID, severity
(Critical / Warning / Info), condition to check, and a recommendation.

The goal is to surface issues that a Marketo ops practitioner would care about during
an audit or handoff — not just data validation, but operational red flags.

Sort findings by severity: Critical first, then Warning, then Info.

If the same rule fires for multiple assets (e.g., three emails are in Draft status),
group them into a single finding with a count rather than listing each separately.

If no flags are detected, note "No issues detected" — this is itself valuable
information.

---

## Step 4: Build the DOCX

**Read `references/document-format.md` now.** Follow the format specification precisely.
Also re-check `references/api-field-mapping.md` for field-to-section mapping.

Use the `docx` npm library.

### Branding

- **Header (content pages only — NOT cover page):** "Program Documentation"
  left-aligned, pink `#dc4393`, 10pt
- **Footer (content pages only — NOT cover page):** Right-aligned — Mary logo
  (`assets/mary-logo.png`, 288 DXA) + "powered by" gray `#888888` 9pt + allGood
  logo (`assets/allgood-logo.png`, 432 DXA). If logos are missing, use text:
  "Mary powered by allGood" in gray.
- **Section headers:** Pink `#dc4393`, Arial 16pt bold

### Document Structure — Cover Page + Six Sections

The document starts with a branded cover page, followed by a page break, then the
six content sections. See `references/document-format.md` for the precise cover page
spec.

---

#### Cover Page (Page 1)

A clean, branded title page with no header/footer. Build it exactly as specified
in the Cover Page section of `references/document-format.md`.

**Content to populate from API data:**

| Element | Source |
|---|---|
| Program code/prefix | Extract date or code prefix from program name if present (e.g., "NL - 2025.03.12" from "NL - 2025.03.12 allGood Customer Newsletter"). If no prefix, omit this line. |
| Program name | Full program name, or the descriptive portion after any prefix |
| Channel pill | `channel` value |
| Type pill | `type` value (e.g., "Email Program", "Default Program") |
| Status pill | `status` value |
| Program ID | `id` |
| Workspace | `workspace` |
| Generated date | Today's date (MM/DD/YYYY) |
| Folder | `folder.folderName` or `folder.value` |
| Last Modified | `updatedAt` formatted as MM/DD/YYYY |

Insert a **page break** after the cover page before starting Section 1.

---

#### Section 1: Overview

**Table type:** Key-Value Table (2-column)

| Field | Source |
|---|---|
| Program Name | `name` |
| Program Type | `type` (Default / Email / Event / Engagement) |
| Channel | `channel` |
| Purpose | `description` — if null, show *"Not set"* in italic gray and flag HC-01 |
| Status | `status` |
| Folder | `folder.value` |
| Workspace | `workspace` |
| Created | `createdAt` formatted as MM/DD/YYYY |
| Last Modified | `updatedAt` formatted as MM/DD/YYYY |

---

#### Section 2: Configuration

**Table type:** Key-Value Table (2-column)

| Field | Source |
|---|---|
| Tags | One row per tag: "Tag Type: Tag Value". If no tags, show *"No tags assigned"* |
| Period Cost | From `costs[]` array: "Start Date: $Amount (Note)". If empty, *"No period cost defined"* |
| SFDC Campaign Sync | If `sfdcId` present: "Synced (ID: [sfdcId])". If null: *"Not synced"* |
| Success Status | Infer from channel configuration if available, otherwise *"Review in Marketo"* |

---

#### Section 3: Asset Inventory

This section has multiple sub-tables for different asset types. Use a sub-heading
(bold 13pt, dark gray `#666666`) before each asset group.

**Sub-section: Smart Campaigns**
**Table type:** Asset Inventory Table (4-column with pink row numbers)

| # | Name | Type | Status |
|---|---|---|---|
| 1 | Campaign Name | Trigger / Batch / Executable | Active / Inactive |

**Sub-section: Emails**
**Table type:** Asset Inventory Table (4-column)

| # | Name | Subject Line | Status |
|---|---|---|---|
| 1 | Email Name | Subject line text | Approved / Draft |

Include from name and operational flag in the Details column if relevant.

**Sub-section: Landing Pages**
If any LPs were found, list them with name, URL, and status.

**Sub-section: Forms**
If any forms were found, list them with name, field count, and global/local indicator.

**Sub-section: Smart Lists & Static Lists**
If any lists were found, list them with name and type.

**Sub-section: My Tokens**
**Table type:** Token Table (3-column)

| Token Name | Type | Value |
|---|---|---|
| `{{my.SubjectLine}}` | text | Current value (truncated at 200 chars) |

For rich text tokens, strip HTML tags and show plain text with a "(rich text)" note.
Flag tokens with placeholder or empty values using italic gray styling.

---

#### Section 4: Program Logic Flow

This is the most valuable section — it documents what the program actually *does*.

For each smart campaign, create a **Smart Campaign Detail Block**:

**Campaign header:** Full-width row with campaign name, type (Trigger/Batch/Executable),
and status (Active/Inactive). Pink left border, bold 12pt.

**Smart List (Triggers & Filters):**

Show the criteria that qualify people for this campaign:

```
TRIGGERS:
  • [Trigger Name]: [Attribute] [Operator] [Value]

FILTERS:
  1. [Filter Name]: [Attribute] [Operator] [Value]
  2. [Filter Name]: [Attribute] [Operator] [Value]
  Logic: [AND / OR / Advanced: 1 and (2 or 3)]
```

Use the data from `get_smart_list_by_campaign_id` with `includeRules=true`.

**Flow Steps:**

Show every flow step in order:

```
FLOW STEPS:
  1. [Action Name] — [Details/Parameters]
     Choice 1: If [condition] → [action]
     Choice 2: If [condition] → [action]
     Default: [action]
  2. Wait — [Duration]
  3. [Action Name] — [Details/Parameters]
```

Use the data from `get_smart_campaign_by_id` with `includeFlowSteps=true`.

**Qualification & Schedule:**

- Qualification rules: Once / Every time / Once every N days
- Schedule (batch campaigns): recurrence details, next run
- Requestable: Yes/No (for executable campaigns)

If a campaign has no flow steps or no smart list rules, document that fact — it is
itself a red flag (HC-13, HC-14).

After all individual campaigns, add a brief **Program Flow Summary** paragraph that
narratively describes: how people enter the program → what happens to them → how they
exit or reach success status. This ties the individual campaign details into a coherent
story.

---

#### Section 5: Health / QA Flags

**Table type:** Health Flag Table (3-column with severity colors)

| Severity | Flag | Recommendation |
|---|---|---|
| Critical | [Flag description] | [What to do about it] |
| Warning | [Flag description] | [What to do about it] |
| Info | [Flag description] | [What to do about it] |

Severity cell colors:
- **Critical:** Red `#DC3545` background, white text
- **Warning:** Orange `#F39C12` background, white text
- **Info:** Blue `#4A90D9` background, white text

If no flags were detected, show a single row:
"No issues detected — program configuration looks healthy" with a green `#28A745`
background.

---

#### Section 6: Performance Snapshot

**Table type:** Key-Value Table (2-column)

If membership/performance data is available from the program details response, include:

| Field | Value |
|---|---|
| Total Members | [count] |
| New Names | [count] |
| Success Count | [count] |
| Success Rate | [percentage] |

If performance data is not available in the API response (it often requires separate
Lead Database API calls with pagination), show:

*"Performance metrics require separate Marketo reporting. Review Program Analyzer
or the Email Performance Report in Marketo for engagement data (open rates, click
rates, conversions)."*

---

### Output

Save to `/mnt/user-data/outputs/<program-name>-documentation.docx`
(sanitize: lowercase, hyphens, no special chars).

---

## Step 5: Validation Checklist

After generating the DOCX, verify every item. Fix any failures before delivering.

**Cover page:**
- [ ] Cover page is Page 1 with NO header/footer
- [ ] Mary logo centered near top of page
- [ ] "powered by" + allGood logo centered below Mary logo
- [ ] Pink horizontal rule (`#dc4393`, 2pt)
- [ ] "PROGRAM DOCUMENTATION" eyebrow label in pink, centered, uppercase
- [ ] Program name in large bold type, centered
- [ ] 3-cell pill table: Channel | Type | Status — centered, pink text, light gray bg
- [ ] Second pink horizontal rule
- [ ] Metadata line: Program ID | Workspace | Generated date — centered, gray
- [ ] Second metadata line: Folder | Last Modified — centered, gray
- [ ] Bottom of page: "For internal use only - Generated by Mary, powered by allGood"
- [ ] Page break after cover page before Section 1

**Structure:**
- [ ] All 6 sections present (Overview, Configuration, Asset Inventory, Program Logic
      Flow, Health/QA Flags, Performance Snapshot)
- [ ] Every section has content — no blank sections (use "No data" notes if needed)
- [ ] Smart campaign detail blocks present for each campaign found
- [ ] Flow steps documented for each campaign (or noted as empty if none exist)
- [ ] Smart list criteria documented for each campaign

**Data accuracy:**
- [ ] All API data represented — no silently dropped fields
- [ ] Null/missing data shown as *"Not set"* in italic gray, not left blank
- [ ] Token values match API response exactly
- [ ] Rich text tokens show plain text with "(rich text)" note
- [ ] Dates formatted as MM/DD/YYYY
- [ ] Cost values formatted as $X,XXX.XX
- [ ] Token values truncated at 200 chars in tables with "..."

**Branding & layout:**
- [ ] Header shows "Program Documentation" left-aligned in pink `#dc4393` (content pages only)
- [ ] Footer shows right-aligned: Mary logo + "powered by" + allGood logo (content pages only)
- [ ] Page margins: 1" top/bottom (1440 DXA), 0.75" left/right (1080 DXA)
- [ ] Arial font used throughout
- [ ] Table widths are 10,320 DXA
- [ ] Section headers are pink `#dc4393`, 16pt, bold
- [ ] Alternating row backgrounds applied (white / `#efefef`)
- [ ] All borders: single, 1pt, `#CCCCCC`
- [ ] Cell margins applied: 100-120 DXA top/bottom, 140 DXA left/right

**Health flags:**
- [ ] Severity colors applied correctly (red Critical / orange Warning / blue Info)
- [ ] All detected flags present in Section 5
- [ ] Recommendations are actionable and specific

If any check fails, fix it and re-validate before delivering the file.
