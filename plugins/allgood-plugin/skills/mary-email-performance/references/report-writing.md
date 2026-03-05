# Report Writing Guide — DOCX Structure & Voice
## Marketo Email Performance Report

---

## Table of Contents
1. [Voice & Tone](#1-voice--tone)
2. [DOCX Structure — Full Spec](#2-docx-structure)
3. [Branding & Visual Spec](#3-branding--visual-spec)
4. [Table Formatting Standards](#4-table-formatting-standards)
5. [Traffic Light Display](#5-traffic-light-display)
6. [Writing Each Section](#6-writing-each-section)

---

## 1. Voice & Tone

Mary is allGood's AI Digital Worker. She does the work — analysis, synthesis,
recommendations — and presents findings as her own. She is not a tool reporting
data; she is a colleague presenting insights. Always attribute work to
"allGood | Mary" (e.g. "allGood | Mary analyzed...").

**Voice principles:**
- Confident and direct. Mary has done the analysis; she states what she found.
  Not "it appears that..." but "Open rates declined 18% across the nurture series."
- Helpful, not alarming. Red flags are presented as opportunities, not crises.
  "This is worth fixing" not "this is a serious problem."
- Specific always. Never say "some emails underperformed." Say which ones, by how much,
  and why it matters.
- Human-scaled. Mary translates numbers into meaning. Not just "CTR is 1.2%"
  but "for every 1,000 emails delivered, about 12 people clicked through."
- First-person plural for recommendations: "We recommend..." — Mary is a partner,
  not an auditor delivering a verdict.

**Tone by section:**
- Cover / Title Block: clean and professional. No filler text.
- Executive Summary: clear and decisive. One read should tell the whole story.
- Key Findings: factual, specific, organized by severity.
- Action Plan: constructive and action-oriented. Always "here's what to do"
  not just "here's what's wrong."

---

## 2. DOCX Structure

Build the document in this exact section order. Use the `docx` npm library.
See the DOCX skill for all technical implementation details (ImageRun, Table,
Header/Footer, etc.).

### Page Budget

Target length: 2 content pages + 1 appendix page (3 pages total)
- **Page 1:** Title block, Executive Summary (narrative + Program Snapshot + Key Metrics
  vs Benchmarks table + Key Findings)
- **Page 2:** Performance by Campaign Type table, Action Plan (all tiers)
- **Page 3 (Appendix):** Success Metrics / 90-Day Targets, Low Volume emails table

### Cover Page / Title Block

```
[Centered, vertically positioned ~40% down the page]

Title (large, bold, pink #dc4393):
"Email Performance Report"

Subtitle (13pt, #666666):
"Analysis Date: [date] | Dataset: [N] campaigns, [X]M emails sent"

[mary-logo.png centered above or beside title]

[Bottom of page, centered]
"Powered by allGood" + allgood-logo.png
```

No filler text — just the title, subtitle, logos, and branding.

### Section 1: Executive Summary (~½ page)

One paragraph of 3–5 sentences that tells the full story. Include:
- Total emails analyzed (excluding low-volume)
- Overall program health score with the emoji (🟢 / 🟡 / 🔴)
- The single most important positive finding
- The single most important issue requiring action
- One forward-looking sentence

Then a **Program Snapshot table** — 2 columns, ~6 rows:

| Metric | Your Program |
|---|---|
| Emails Analyzed | N (+ X low volume excluded) |
| Total Sent (≥100 sends) | X,XXX,XXX |
| Overall Delivery Rate | XX.X% 🟢/🟡/🔴 |
| Weighted Open Rate | XX.X% 🟢/🟡/🔴 |
| Weighted CTR | X.X% 🟢/🟡/🔴 |
| Weighted Unsubscribe Rate | X.XX% 🟢/🟡/🔴 |

Then a **Key Metrics vs Benchmarks table** — comparing program-level weighted
metrics to SaaS averages and healthy targets (consolidates the former standalone
Benchmarks Comparison section):

| Metric | This Program | SaaS Avg | Healthy Target | Status |
|---|---|---|---|---|
| Delivery Rate | | 94–97% | > 98% | 🟢/🟡/🔴 |
| Open Rate (marketing) | | 19–25% | 25–35% | |
| CTR (marketing) | | 1.2–1.9% | 2–2.5% | |
| Click-to-Open Rate | | 8–12% | 10–15% | |
| Unsubscribe Rate | | 0.1–0.2% | < 0.15% | |

Include a brief note below the table about the MPP caveat on open rates and
bot-click caveat on CTR, written in Mary's voice.

Then **Key Findings** — tight bullets organized into three tiers.
Maximum 10 findings total. Each finding is 1–2 sentences: what was observed + why
it matters.

**Strengths** (genuine positives worth calling out)
**Risks** (🔴 items + 🟡 patterns needing attention)
**Notable** (A/B test takeaways, series funnel insights, anomalies)

Roll the top 5 worst-performing emails (🔴) into the Risks bullets with specific
metrics and thresholds breached.

Never invent positives. If everything is in Caution territory, say so honestly:
"There are no standout performers yet — the program has room to grow across the board."

### Section 2: Performance by Campaign Type

One compact table with one row per detected email type. Keep narrative to a single
summary sentence above the table (e.g. "allGood | Mary analyzed X emails across
Y campaign types.").

**Table format:**

| Campaign Type | Count | Avg Open Rate | Avg CTR | Avg CTOR | Avg Unsub | vs Benchmark |
|---|---|---|---|---|---|---|
| [Type] | N | XX% | X.X% | XX% | X.XX% | 🟢/🟡/🔴 |

If a campaign series exists within a type, include a compact funnel sub-table:

| Email | Sent | Open Rate | CTR | Unsub | vs. Prior |
|---|---|---|---|---|---|
| Email 1 | X,XXX | XX% | X.X% | X.XX% | — |
| Email 2 | X,XXX | XX% | X.X% | X.XX% | ↓ X% |

### Section 3: Action Plan

Structured as a compact table grouped by priority tier. Maximum 8 recommendations
total across all tiers. Prioritize 🔴 flags first.

**Critical (🔴) — Do This Week**

| Priority | Action | Expected Impact |
|----------|--------|-----------------|
| 🔴 #1 | One-liner description of the action | One-liner expected outcome |
| 🔴 #2 | ... | ... |

**High Priority (🟡) — Next 30 Days**

| Priority | Action | Expected Impact |
|----------|--------|-----------------|
| 🟡 #3 | ... | ... |

**Medium-Strategic — Next 90 Days**

| Priority | Action | Expected Impact |
|----------|--------|-----------------|
| #5 | ... | ... |

Each action must be specific and data-backed — not "improve subject lines" but
"A/B test subject lines on [specific campaign] where OR is X% below benchmark."

### Appendix

**Success Metrics / 90-Day Targets** — a table of target metrics the program should
aim for over the next quarter, based on the current baseline and healthy targets:

| Metric | Current | 30-Day Target | 90-Day Target |
|---|---|---|---|
| Open Rate | XX% | XX% | XX% |
| CTR | X.X% | X.X% | X.X% |
| Unsubscribe Rate | X.XX% | X.XX% | X.XX% |

**Low Volume Emails** — a simple table listing all emails with Sent < 100:

| Email Name | Sent | Delivered | Open Rate | Note |
|---|---|---|---|---|
| [Name] | X | X | X% | Low volume — excluded from analysis |

Include one sentence: "These emails were excluded from all program averages and
benchmarks due to insufficient send volume for statistical significance."

---

## 3. Branding & Visual Spec

**Logo files:**
- `assets/mary-logo.png` — Mary's logo. Circular with pink `#dc4393` border.
  Used on cover page, centered above or beside the title.
  Target display size: ~1.5 inches. If missing, insert a placeholder box
  labeled "MARY LOGO PLACEHOLDER" with a light gray border.
- `assets/allgood-logo.png` — allGood logo. Used in footer on every page,
  centered next to "Powered by allGood". If missing, insert labeled placeholder.

**Page Setup:**
| Property | Value | Notes |
|---|---|---|
| Page Margins (Top/Bottom) | 1 inch (1440 DXA) | Standard margins |
| Page Margins (Left/Right) | 0.75 inch (1080 DXA) | Slightly narrower for wider tables |
| Total Table Width | 10320 DXA | Fills page width within margins |
| Default Font | Arial | Used throughout |
| Default Font Size | 11pt (22 half-points) | Body text size |

**Color Palette:**
| Element | Hex | Usage |
|---|---|---|
| Pink/Magenta | `#dc4393` | Section headings, row number cells background |
| Light Gray | `#efefef` | Alternating row backgrounds |
| Lighter Gray | `#f3f3f3` | Special rows (e.g. cover subtitle) |
| White | `#FFFFFF` | Alternating row backgrounds |
| Dark Gray (text) | `#666666` | Token text, table header backgrounds |
| Medium Gray (text) | `#888888` | Helper text, captions, footnotes |
| White Text | `#FFFFFF` | Text on dark/pink backgrounds |
| Border Gray | `#CCCCCC` | All table cell borders |

**Traffic light row highlights** (used in performance tables):
| Status | Fill Color |
|---|---|
| 🟢 Healthy | `#E8F5E9` (light green) |
| 🟡 Caution | `#FFFDE7` (light yellow) |
| 🔴 Action Required | `#FFEBEE` (light red) |

**Typography:**
- Font: Arial throughout
- H1 (section titles): 18pt, bold, `#dc4393` (pink/magenta)
- H2 (subsections): 13pt, bold, `#666666` (dark gray)
- Body: 11pt, `#333333`
- Table header text: 10pt, bold, white (`#FFFFFF`) on `#666666` background
- Table body text: 10pt, `#333333`
- Footer: 9pt, `#888888`

**Typography rules:**
- Section headings use `#dc4393` — this is the primary brand color, use it
  consistently for all H1-level section titles
- Table headers always use white text on `#666666` dark gray background
- Row numbers or index cells (where used) use white text on `#dc4393` background
- Never use navy or blue — those are not allGood brand colors

---

## 4. Table Formatting Standards

- Always use `WidthType.DXA` — never percentages
- **Total table width: 10,320 DXA** (page width at 0.75" left/right margins)
- Header rows: `#666666` fill, white bold text, `ShadingType.CLEAR`
- Alternating rows: white (`#FFFFFF`) and light gray (`#efefef`)
- Row number / index cells: white text on `#dc4393` pink background
- Status rows: use traffic light fills from Section 3 above
- Cell padding: `{ top: 80, bottom: 80, left: 120, right: 120 }`
- All borders: `BorderStyle.SINGLE`, size 1, color `#CCCCCC`

**Standard column widths for the Campaign Type table (total: 10,320 DXA):**
Campaign Type: 2,200 | Count: 800 | Open Rate: 1,400 | CTR: 1,200 |
CTOR: 1,200 | Unsub: 1,200 | vs Benchmark: 2,320
Total: 10,320 ✓

---

## 5. Traffic Light Display

In tables, use emoji: 🟢 🟡 🔴
In running text, spell out: "Healthy", "Caution", "Action Required"
In the Key Findings bullets, always include the specific number and threshold,
not just the emoji.

For the Status column in tables, show only the emoji for space.

---

## 6. Writing Each Section

**Executive Summary — what to avoid:**
- "Overall, the email program shows mixed results" — too vague
- "Several emails are underperforming" — which ones? by how much?
- Listing every finding — that's what Key Findings is for

**Key Findings — what to avoid:**
- More than 10 bullets
- Findings without numbers
- Negative-only tone — always include at least one genuine strength

**Action Plan — what to avoid:**
- "Improve subject lines" — too vague
- "Consider A/B testing" — too passive; say what to test and why
- More than 8 total — a prioritized short list beats an exhaustive long one
- Recommendations that aren't supported by the data
- Paragraph-block format — use the compact table format instead
