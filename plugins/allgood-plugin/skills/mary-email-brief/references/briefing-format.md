# Campaign Briefing Document — Format Specification

This is the complete formatting reference for building campaign briefing DOCX files.
Follow it precisely when constructing tables, labels, and layout.

---

## Page Setup

| Property | Value | Notes |
|---|---|---|
| Page Margins (Top/Bottom) | 1 inch (1440 DXA) | Standard margins |
| Page Margins (Left/Right) | 0.75 inch (1080 DXA) | Slightly narrower for wider tables |
| Total Table Width | 10320 DXA | Fills page width within margins |
| Default Font | Arial | Used throughout |
| Default Font Size | 11pt (22 half-points) | Body text size |

---

## Color Palette

| Element | Hex Code | Usage |
|---|---|---|
| Pink/Magenta | `#dc4393` | Row number cells background, section headings |
| Light Gray | `#efefef` | Alternating row backgrounds |
| Lighter Gray | `#f3f3f3` | Special rows (e.g., greeting rows) |
| White | `#FFFFFF` | Alternating row backgrounds |
| Dark Gray (text) | `#666666` | Token text |
| Medium Gray (text) | `#888888` | Helper text |
| Dark Gray (bg) | `#666666` | Content table header rows |
| White Text | `#FFFFFF` | Text on dark backgrounds |
| Border Gray | `#CCCCCC` | Table cell borders |

---

## Section Headers

- **Style:** Heading 2
- **Font:** Arial, 16pt (32 half-points)
- **Weight:** Bold
- **Color:** Pink (`#dc4393`)
- **Spacing:** 400 DXA before, 200 DXA after

**Section Types:**

1. Program Details
2. Shared Content: Event Details (or other shared content type)
3. Email 1 Content / Email 2 Content / Email 3 Content
4. Landing Page Content

**Optional Sub-label:** Below each section header, add an italic descriptor in gray
(`#666666`, 10pt):

```
Email 1 Content
Announcement — Introducing Campaign Management
```

---

## Field Label Structure (Three-Line Format)

**CRITICAL:** Each field uses a **three-line structure** in the label column:

| Line | Content | Formatting |
|---|---|---|
| **Line 1** | User-friendly field name | Bold, 11pt (22 half-points), Black |
| **Line 2** | Marketo token | Regular, 9pt (18 half-points), Gray (`#666666`) |
| **Line 3** | Helper text / guidance | Italic, 8pt (16 half-points), Light Gray (`#888888`) |

**Example:**

```
Subject Line                    ← Line 1: Bold, 11pt, Black
{{my.SubjectLine}}              ← Line 2: Regular, 9pt, Gray
40-65 characters                ← Line 3: Italic, 8pt, Light Gray
```

**Spacing:**

- 40 DXA after Line 1
- 40 DXA after Line 2 (if Line 3 exists)
- No spacing after Line 3

---

## User-Friendly Label Names

Always use clear, human-readable names on Line 1. The token name goes on Line 2.

| User-Friendly Name (Line 1) | Token (Line 2) | Helper Text (Line 3) |
|---|---|---|
| Subject Line | `{{my.SubjectLine}}` | 40-65 characters |
| Preheader | `{{my.Preheader}}` | 40-100 characters |
| Banner Image | `{{my.Banner}}` | Recommended: 600x200px |
| Banner URL | `{{my.BannerURL}}` | Please build your UTM |
| Headline | `{{my.Headline}}` | *(optional)* |
| Greeting | `{{my.Greeting-em1}}` | e.g. Hi / Hello / Hey |
| First Name | `{{lead.FirstName}}` | Personalization token |
| Body Copy | `{{my.Copy}}` | Main email body |
| CTA Button Text | `{{my.CTA1Text}}` | ALL CAPS recommended |
| CTA Button URL | `{{my.CTA1URL}}` | Please build your UTM |
| Secondary Copy | `{{my.Copy2}}` | Below CTA content |
| Event Type | `{{my.EventType}}` | *(optional)* |
| Event Title | `{{my.EventTitle}}` | *(optional)* |
| Event Date | `{{my.EventDate}}` | Format: MM/DD/YYYY |
| Event Time | `{{my.EventTime}}` | Include timezone |
| Event Location | `{{my.EventLocation}}` | *(optional)* |
| Landing Page URL | `{{my.RegLPURL}}` | Please build your UTM |

**For multi-email campaigns, prefix tokens with email number:**

- Email 1: `{{my.SubjectLine}}`, `{{my.Copy}}`
- Email 2: `{{my.em2-SubjectLine}}`, `{{my.em2-Copy}}`
- Email 3: `{{my.em3-SubjectLine}}`, `{{my.em3-Copy}}`

---

## Table Types

### Type 1: Instructions Box (Single Column)

Used for operational instructions at the top of the document.

| Property | Value |
|---|---|
| Columns | 1 |
| Width | 10320 DXA (full width) |
| Header Row Background | Light Gray (`#efefef`) |
| Header Text | Bold, 12pt (24 half-points) |
| Body Cell Background | White |
| Cell Margins | Top/Bottom: 120 DXA, Left/Right: 140 DXA |

**Content Structure:**

- Header row with title (e.g., "Mary Instructions")
- Body row with numbered lists and instructions
- Use separate numbered list references for each list section (so numbering restarts)

---

### Type 2: Two-Column Table (Subject/Preheader & Event Basics)

Used for subject lines, preheaders, and simple field/value pairs.

| Property | Value |
|---|---|
| Columns | 2 |
| Column 1 Width | 4200 DXA (Label column) |
| Column 2 Width | 6120 DXA (Value column) |
| Total Width | 10320 DXA |
| Row Background | Alternating: White → Gray (`#efefef`) → White... |
| Cell Margins | Top/Bottom: 120 DXA, Left/Right: 140 DXA |
| Borders | Single, 1pt, Gray (`#CCCCCC`) on all sides |

**Column 1 Structure (Three-Line Format):**

```
Line 1: Subject Line          — Bold, 11pt, Black
Line 2: {{my.SubjectLine}}    — Regular, 9pt, Gray (#666666)
Line 3: 40-65 characters      — Italic, 8pt, Light Gray (#888888)
```

**Column 2 Structure:**

```
Value text — Regular, 11pt, Black
```

---

### Type 3: Two-Column Content Table (Email/LP Body Content)

Used for email body content with a dark header row.

| Property | Value |
|---|---|
| Columns | 2 |
| Column 1 Width | 4200 DXA (Label column) |
| Column 2 Width | 6120 DXA (Value/Content column) |
| Total Width | 10320 DXA |
| Header Row (Col 2) | Dark Gray background (`#666666`), White text |
| Row Background | Alternating: Gray (`#efefef`) / White |
| Cell Margins | Top/Bottom: 120 DXA, Left/Right: 140 DXA |

**Header Row:**

| Column 1 | Column 2 |
|---|---|
| *(empty, white bg)* | "Add your copy/image to this column" (white text on dark gray) |

---

### Type 4: Three-Column Table (Numbered Rows)

Used for landing page content and structured content with row numbers.

| Property | Value |
|---|---|
| Columns | 3 |
| Column 1 Width | 720 DXA (Number) |
| Column 2 Width | 4200 DXA (Label + Token) |
| Column 3 Width | 5400 DXA (Value) |
| Total Width | 10320 DXA |
| Row Background | Columns 2-3 Alternating: Gray (`#efefef`) → White → Gray... |
| Cell Margins | Top/Bottom: 120 DXA, Left/Right: 140 DXA |
| Borders | Single, 1pt, Gray (`#CCCCCC`) on all sides |

**Column 1 (Number Cell):**

- Background: Pink (`#dc4393`)
- Text: White (`#FFFFFF`), Bold, 12pt (24 half-points)
- Alignment: Center (horizontal and vertical)
- Content: Row number (e.g., "1", "2a", "2b", "3")

**Column 2 (Three-Line Format):**

```
Line 1: Event Title           — Bold, 11pt, Black
Line 2: {{my.EventTitle}}     — Regular, 9pt, Gray (#666666)
Line 3: *(helper if needed)*  — Italic, 8pt, Light Gray (#888888)
```

**Header Row:**

| Column 1 | Column 2 | Column 3 |
|---|---|---|
| "#" (white on pink) | *(empty)* | "Add your copy/image to this column" (white on dark gray) |

---

### Type 5: Image Placeholder Row

Used to indicate where screenshots should be inserted.

| Property | Value |
|---|---|
| Columns | 1 |
| Width | 10320 DXA (full width) |
| Background | Light Gray (`#efefef`) |
| Cell Margins | Top/Bottom: 200 DXA, Left/Right: 160 DXA |
| Text Spacing | 600 DXA before and after |
| Text Style | Italic, 11pt (22 half-points), Gray (`#666666`) |
| Alignment | Center |

**Content Example:**

```
[IMAGE PLACEHOLDER: Email Screenshot]
```

---

## Visual Marker Number System

The pink numbered column connects table rows to numbered markers on the email/LP
screenshot. This helps users see where each piece of content appears in the final asset.

### Standard Email Number Mapping

| # | Element(s) | Description |
|---|---|---|
| 1 | Subject Line | Email subject in inbox |
| 2 | Preheader | Preview text below subject |
| 3 | Banner Image, Banner URL | Hero image area (grouped) |
| 4 | Headline | Main headline in hero section |
| 5 | Greeting, First Name | Salutation line (grouped) |
| 6 | Body Copy | Main email body content |
| 7 | CTA Button Text, CTA URL | Call-to-action button (grouped) |
| 8 | Secondary Copy | Content below the CTA |

### Grouping Rules

**Same number = Same visual element**

When multiple table rows share the same number:
- They all contribute to a single visual element in the email
- They should have the same row background color
- The number appears in each row

**Examples of grouped elements:**
- **Banner (3):** Image source + Click URL
- **Salutation (5):** Greeting word + First name token
- **CTA Button (7):** Button text + Button URL
- **Event Details (4):** Date + Time + Location (if displayed together)

---

## Token Naming Convention

Tokens follow the Marketo `{{my.XXX}}` format for program tokens and `{{lead.XXX}}`
for lead tokens.

**Program Token Numbering System (for numbered tables):**

| Range | Section |
|---|---|
| 001-099 | Event Basics / Shared Content |
| 101-199 | Email Content / Email 1 |
| 201-299 | Landing Page Content / Email 2 |
| 300+ | Post-Event Emails / Email 3 |

**Multi-Email Token Prefixes:**

| Email | Prefix | Example |
|---|---|---|
| Email 1 | *(none)* | `{{my.SubjectLine}}` |
| Email 2 | `em2-` | `{{my.em2-SubjectLine}}` |
| Email 3 | `em3-` | `{{my.em3-SubjectLine}}` |

**Sub-numbering for Related Fields:**

When a single item has multiple related fields (CTA, Copy, URL), use letter suffixes:
- `{{my.102a Post 1 CTA}}`
- `{{my.102b Post 1 Copy}}`
- `{{my.102c Post 1 URL}}`

---

## Copy Section Formatting (Rich Text Variations)

For Body Copy and Secondary Copy fields, use varied formatting to demonstrate the range
of styling options.

### Alignment Options

| Type | Usage |
|---|---|
| Left | Default body text, standard paragraphs |
| Center | Headlines, callouts, key statements, speaker names |
| Right | Attributions, quotes, alternating style emphasis |

### Font Sizes (in half-points)

| Size | Half-points | Usage |
|---|---|---|
| 8pt | 16 | Helper text, fine print |
| 9pt | 18 | Tokens, small labels |
| 10pt | 20 | Secondary text, attributions |
| 11pt | 22 | Body text (default) |
| 12pt | 24 | Emphasis, row numbers |
| 13pt | 26 | Sub-headlines |
| 14pt | 28 | Headlines |
| 16pt | 32 | Large callouts |

### Text Styling Options

| Style | Usage Example |
|---|---|
| **Bold** | Key terms, feature names, statistics |
| *Italic* | Quotes, speaker text, emphasis |
| Underline (Single) | Links, key phrases |
| Underline (Double) | Strong emphasis headers |
| Underline (Wavy) | Playful emphasis |
| ~~Strikethrough~~ | "Old way" vs "new way" comparisons |
| SMALL CAPS | Job titles, categories |

### Color Palette for Copy

| Color | Hex | Usage |
|---|---|---|
| Blue | `#4A90D9` | Links, feature names, positive callouts |
| Green | `#27AE60` / `#28A745` | Success, results, positive outcomes |
| Red | `#E74C3C` / `#DC3545` | Urgency, pain points, emphasis |
| Purple | `#8E44AD` | Quotes, special callouts |
| Orange/Gold | `#F39C12` | Stars, highlights, awards |
| Dark Gray | `#2C3E50` | Speaker names |
| Medium Gray | `#7F8C8D` | Attributions, secondary text |
| Pink | `#dc4393` | Brand accent callouts |

### Special Characters

| Character | Usage |
|---|---|
| → | List items, results |
| ✦ | Section dividers |
| ★ | Testimonial headers |
| ❌ | Pain points, negative items |
| • | Bullet points |

---

## Row Alternation Pattern

Rows alternate between gray and white backgrounds for readability:

| Row | Background |
|---|---|
| 1 | White (`#ffffff`) or Gray (`#efefef`) — depends on table type |
| 2 | Opposite of Row 1 |
| 3 | Same as Row 1 |
| ... | continues... |

**Note:** In 3-column tables, the pink number column (Column 1) always stays pink
regardless of row alternation.

---

## Document Structure Order

### For Event/Landing Page Campaigns

1. **Program Details** (section header)
   - Instructions Box (Mary Instructions)
2. **Shared Content: Event Details** (section header)
   - 2-column table with core event info (shared across emails and LP)
3. **Email Content** (section header)
   - Helper text about screenshots
   - Image placeholder
   - 3-column or 2-column content table
4. **Landing Page Content** (section header)
   - Helper text about screenshots
   - Image placeholder
   - 3-column numbered table

### For Multi-Touch Email Campaigns

1. **Program Details** (section header)
   - Instructions Box (Mary Instructions)
2. **Email 1 Content** (section header + subtitle)
   - Subject/Preheader table (2-col)
   - Content table with header row (2-col)
3. **Email 2 Content** (section header + subtitle)
   - Subject/Preheader table (2-col)
   - Content table with header row (2-col)
4. **Email 3 Content** (section header + subtitle)
   - Subject/Preheader table (2-col)
   - Content table with header row (2-col)

---

## Spacing Guidelines

| Element | Spacing |
|---|---|
| Between sections | 2 empty paragraphs |
| After section header | Built into heading style (180-200 DXA) |
| After section subtitle | 1 empty paragraph |
| Between tables | 1 empty paragraph |
| Inside cells (after Line 1) | 40 DXA |
| Inside cells (after Line 2) | 40 DXA (if Line 3 exists) |

---

## Cell Margins

| Table Type | Top/Bottom | Left/Right |
|---|---|---|
| Instructions Box | 100-120 DXA | 140 DXA |
| 2-Column Tables | 120 DXA | 140 DXA |
| 3-Column Tables | 120 DXA | 140 DXA |
| Image Placeholder | 200 DXA | 160 DXA |

---

## Technical Notes (for docx-js implementation)

### Cell Margins

```javascript
margins: { top: 120, bottom: 120, left: 140, right: 140 }
```

### Border Definition

```javascript
const tableBorder = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const cellBorders = {
  top: tableBorder,
  bottom: tableBorder,
  left: tableBorder,
  right: tableBorder
};
```

### Shading (Background Color)

```javascript
shading: { fill: "efefef", type: ShadingType.CLEAR }
```

**Important:** Always use `ShadingType.CLEAR`, never `ShadingType.SOLID`.

### Font Sizes (in half-points)

| Points | Half-points | Usage |
|---|---|---|
| 8pt | 16 | Helper text (Line 3) |
| 9pt | 18 | Token text (Line 2) |
| 10pt | 20 | Attributions, subtitles |
| 11pt | 22 | Body text (default) |
| 12pt | 24 | Headers, row numbers |
| 13pt | 26 | Sub-headlines |
| 14pt | 28 | Section headlines |
| 16pt | 32 | Large callouts |

### Underline Types

```javascript
underline: { type: UnderlineType.SINGLE }   // Standard
underline: { type: UnderlineType.DOUBLE }   // Strong emphasis
underline: { type: UnderlineType.WAVY }     // Playful
underline: { type: UnderlineType.THICK }    // Heavy emphasis
```

### Numbered Lists (Restart Numbering)

Use separate `reference` names for each numbered list section to restart numbering:

```javascript
{ reference: "numbered-list-1", level: 0 }  // First list: 1, 2, 3
{ reference: "numbered-list-2", level: 0 }  // Second list: restarts at 1
{ reference: "bullet-list-1", level: 0 }    // First bullet list
```

---

## Quick Reference Checklist

When creating a new briefing document:

- [ ] Set page margins (1" top/bottom, 0.75" left/right)
- [ ] Use Arial font throughout
- [ ] Apply pink color (`#dc4393`) to section headers
- [ ] Create instructions box with gray header
- [ ] **Add screenshot placeholder before content tables**
- [ ] **Use 3-column tables with pink number column:**
      - [ ] Column 1: Number (pink background, white text)
      - [ ] Column 2: Label + Token + Helper
      - [ ] Column 3: Value/Content
- [ ] **Group related fields under the same number:**
      - [ ] Banner Image + Banner URL = same #
      - [ ] Greeting + First Name = same #
      - [ ] CTA Text + CTA URL = same #
- [ ] Use 3-line label structure in Column 2
- [ ] Alternate row backgrounds (gray/white)
- [ ] For copy sections, include varied formatting
- [ ] Follow token naming convention
- [ ] Add cell margins for breathing room (120 DXA top/bottom, 140 DXA left/right)
- [ ] Header: "Campaign Briefing" left-aligned in pink
- [ ] Footer: right-aligned single line — Mary logo + "powered by" + allGood logo
