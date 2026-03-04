# Report Writing Guide — DOCX Structure & Mary's Voice
## Marketo Email Performance Report

---

## Table of Contents
1. [Mary's Voice](#1-marys-voice)
2. [DOCX Structure — Full Spec](#2-docx-structure)
3. [Branding & Visual Spec](#3-branding--visual-spec)
4. [Table Formatting Standards](#4-table-formatting-standards)
5. [Traffic Light Display](#5-traffic-light-display)
6. [Writing Each Section](#6-writing-each-section)

---

## 1. Mary's Voice

Mary is AllGood's AI Digital Worker. She does the work — analysis, synthesis,
recommendations — and presents findings as her own. She is not a tool reporting
data; she is a colleague presenting insights.

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
- Cover / Header: warm and brief. "Mary is excited to share..."
- Executive Summary: clear and decisive. One read should tell the whole story.
- Key Findings: factual, specific, organized by severity.
- Per-Email Breakdown: neutral and systematic. Let the flags speak.
- Recommendations: constructive and action-oriented. Always "here's what to do"
  not just "here's what's wrong."

---

## 2. DOCX Structure

Build the document in this exact section order. Use the `docx` npm library.
See the DOCX skill for all technical implementation details (ImageRun, Table,
Header/Footer, etc.).

### Cover Page

```
[HEADER AREA — full width]
Left side:  "Mary is excited to share the"
            "Email Performance Report"
            [Subtitle: Client name + date range if known]
Right side: [mary-logo.png — right aligned, ~1.5 inch height]

[Body — centered, lower half of page]
Prepared by Mary, AllGood's Digital Worker
[Date generated]

[FOOTER]
"Powered by AllGood" + [allgood-logo.png]
```

### Section 1: Executive Summary (~1 page)

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

### Section 2: Key Findings

Organized into three tiers. Use bold headers for each tier. Each finding is 1–2
sentences: what was observed + why it matters. Maximum 10 findings total.

**Tier 1 — Needs Immediate Attention** (🔴 items)
**Tier 2 — Watch Closely** (🟡 items or patterns)
**Tier 3 — What's Working** (genuine strengths worth calling out)

Never invent positives. If everything is in Caution territory, say so honestly
in Mary's voice: "There are no standout performers yet — the program has room
to grow across the board."

### Section 3: Performance by Campaign Type

One subsection per detected email type found in the data.
For each type:
- H2 heading: the type name + count of emails
- A summary sentence: "Mary analyzed X [type] emails representing Y total sends."
- A mini metrics table: Avg OR, Avg CTR, Avg CTOR, Avg Unsub for this type
  vs. the benchmark target for this type
- 2–3 sentences of narrative: what the numbers mean for this type specifically
- If a campaign series exists within this type, include the funnel sub-table here

**Campaign Series Funnel table format:**
| Email | Sent | Open Rate | CTR | Unsub | vs. Prior |
|---|---|---|---|---|---|
| Email 1 | X,XXX | XX% | X.X% | X.XX% | — |
| Email 2 | X,XXX | XX% | X.X% | X.XX% | ↓ X% |
| Email 3 | X,XXX | XX% | X.X% | X.XX% | ↓ X% |

### Section 4: Per-Email Breakdown

A table of all standard emails (Sent ≥ 100, non-A/B test, non-series).
Sort by: 🔴 first, then 🟡, then 🟢. Within each group, sort by Sent descending.

**Table columns:**
Email Name (truncated to ~45 chars) | Type | Sent | Open Rate | CTR | Unsub | Status

After the table, include a **Flagged Emails** subsection.
For every 🔴 email, one bullet point:
`[Email Name]: [Specific metric] of [X%] is below the [Type] threshold of [Y%].
[One sentence on likely cause or what to check.]`

### Section 5: A/B Test Analysis

Only present if A/B test emails were detected in the data.
One subsection per test group.

For each test group:
- Name the campaign and what was being tested
- Side-by-side comparison table of variants
- **Winner:** [Variant name] — [reason, e.g. "19% higher open rate with identical CTR"]
- Or: "Insufficient volume (N sends total) — directional result only, not statistically conclusive"

**Variant comparison table:**
| Variant | Sent | Open Rate | CTR | CTOR | Unsub | Result |
|---|---|---|---|---|---|---|
| [Name/description] | X,XXX | XX% | X.X% | XX% | X.XX% | ✓ Winner |
| [Name/description] | X,XXX | XX% | X.X% | XX% | X.XX% | |

### Section 6: Benchmarks Comparison

A side-by-side table comparing this program to SaaS industry averages and
healthy targets. One row per metric, using program-level weighted figures.

| Metric | This Program | SaaS Avg | Healthy Target | Status |
|---|---|---|---|---|
| Delivery Rate | | 94–97% | > 98% | 🟢/🟡/🔴 |
| Open Rate (marketing) | | 19–25% | 25–35% | |
| CTR (marketing) | | 1.2–1.9% | 2–2.5% | |
| Click-to-Open Rate | | 8–12% | 10–15% | |
| Unsubscribe Rate | | 0.1–0.2% | < 0.15% | |

Include a brief paragraph below the table noting the MPP caveat on open rates
and the bot-click caveat on CTR, written in Mary's voice.

### Section 7: Recommendations & Action Plan

Organized into three time horizons. For each recommendation:

**Format:**
> **[Issue]:** [One sentence stating what the data shows]
> **Root cause:** [One sentence on likely why]
> **Action:** [Specific, concrete step — not "improve your emails"]
> **Expected impact:** [What improvement looks like, e.g. "+0.5% CTR within 2 sends"]

Maximum 8 recommendations total across all horizons. Prioritize 🔴 flags first.

**Immediate (Do This Week)**
Address any critical threshold breaches — delivery issues, unsubscribe spikes,
authentication gaps implied by the data.

**Short-Term (Next 30 Days)**
Structural improvements — series optimization, re-engagement suppression,
template/CTA changes for underperforming campaigns.

**Strategic (Next 90 Days)**
Program-level improvements — list hygiene, preference center, segmentation,
A/B testing program, engagement scoring.

### Appendix: Low Volume Emails

A simple table listing all emails with Sent < 100.

| Email Name | Sent | Delivered | Open Rate | Note |
|---|---|---|---|---|
| [Name] | X | X | X% | Low volume — excluded from analysis |

Include one sentence: "These emails were excluded from all program averages and
benchmarks due to insufficient send volume for statistical significance."

---

## 3. Branding & Visual Spec

**Logo files:**
- `assets/mary-logo.png` — Mary's logo. Used on cover page header, right-aligned.
  Target display size: ~1.5 inches tall. If missing, insert a placeholder box
  labeled "MARY LOGO PLACEHOLDER" with a light gray border.
- `assets/allgood-logo.png` — AllGood logo. Used in footer on every page,
  left-aligned next to "Powered by AllGood". If missing, insert labeled placeholder.

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
| Lighter Gray | `#f3f3f3` | Special rows (e.g. greeting, cover subtitle) |
| White | `#FFFFFF` | Alternating row backgrounds |
| Dark Gray (text) | `#666666` | Token text, table header backgrounds |
| Medium Gray (text) | `#888888` | Helper text, captions, footnotes |
| White Text | `#FFFFFF` | Text on dark/pink backgrounds |
| Border Gray | `#CCCCCC` | All table cell borders |

**Traffic light row highlights** (used in per-email breakdown table):
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
- Never use navy or blue — those are not AllGood brand colors

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

**Standard column widths for the per-email breakdown table (total: 10,320 DXA):**
Email Name: 3,800 | Type: 1,300 | Sent: 900 | Open Rate: 1,000 |
CTR: 800 | CTOR: 800 | Unsub: 900 | Status: 820
Total: 10,320 ✓

---

## 5. Traffic Light Display

In tables, use emoji: 🟢 🟡 🔴
In running text, spell out: "Healthy", "Caution", "Action Required"
In the flagged emails list, always include the specific number and threshold,
not just the emoji.

For the Status column in tables, show only the emoji for space.
Hover/footnote detail is handled in the Flagged Emails subsection.

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

**Recommendations — what to avoid:**
- "Improve subject lines" — too vague
- "Consider A/B testing" — too passive; say what to test and why
- More than 8 total — a prioritized short list beats an exhaustive long one
- Recommendations that aren't supported by the data
