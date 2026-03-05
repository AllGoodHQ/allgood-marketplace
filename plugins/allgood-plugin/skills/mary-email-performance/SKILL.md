---
name: mary-email-performance
description: >
  Use this skill whenever a user uploads or references a Marketo Email Performance Report
  (XLS, XLSX, or CSV) and wants analysis, a performance report, diagnostics, or recommendations.
  Triggers include: "analyze my email report", "how are my emails performing", "Marketo report",
  "email performance", "build a report from this XLS", or any upload of a file that looks like
  a Marketo email export with columns like Sent, Delivered, Opened, Clicked, Bounced.
  Always use this skill even if the user just says "look at this email data" — if it looks
  like a Marketo export, this skill applies.
---

# Mary - Marketo Email Performance Analyzer

Mary analyzes a Marketo Email Performance Report and produces a structured, branded DOCX
report with executive summary, key findings, benchmark comparisons, and a prioritized
action plan — condensed to 2 pages.

---

## User Request

The user has requested: $ARGUMENTS

Adapt the analysis based on what the user asked:
- **Specific metric mentioned** (e.g. "open rates", "CTR") → lead with that metric,
  give it the most depth in the report, and surface it first in the exec summary
- **Campaign name or filter** (e.g. "just the webinar emails") → filter the dataset
  to matching rows before analysis. Still run the full workflow on the filtered set.
- **"Quick summary" or "just the highlights"** → skip the full DOCX. Instead, respond
  in chat with: program health score, top 3 findings, and top 3 action items.
- **"Break down by campaign type"** or **"show me by type"** → include a Performance
  by Campaign Type table as an additional page after the Action Plan. One row per
  detected email type with metrics vs benchmarks.
- **"Compare X vs Y"** → focus on a side-by-side of the named campaigns or types
- **No specific ask / generic request** → run the full default analysis (all steps)

Always complete Step 0 (file ingestion) and Step 1 (parse) regardless of the request.
The adaptation applies to Steps 2–3.

---

## How to Use This Skill

This skill has three reference files. Load them at the right step — don't load all at once.

| Reference File | Load When |
|---|---|
| `references/benchmarks.md` | Step 2 — during analysis and flagging |
| `references/email-types.md` | Step 1 — during classification |
| `references/report-writing.md` | Step 3 — when building the DOCX |

---

## Step 0: File Ingestion

Marketo exports are typically large (hundreds of rows). Use the Filesystem extension
to copy the file into the working environment for programmatic analysis.

1. Ask the user for the exact filename of their Marketo report
2. Use `Filesystem:copy_file_user_to_claude` to copy it in
3. Verify the file exists and is readable before proceeding
4. If the copy fails, ask the user to confirm their shared drive is connected
   and the file is in their designated Claude folder. If they need setup help,
   point them to: https://www.allgoodhq.com/blog/how-to-use-claude-desktop-for-data-analysis?utm_source=claude

If the user attached a small file directly in chat instead, save it to disk first
so it can be processed with pandas.

Do NOT begin analysis until the file is confirmed on disk and readable by Python.

---

## Step 1: Explore and Parse the Data

Start by exploring the file before assuming anything about its structure. Write and run
Python code (pandas) to:

1. **Discover the schema** — print all column names and a sample row. Map whatever columns
   exist to the expected fields (Sent, Delivered, Opened, Clicked, Bounced, Unsubscribed,
   % variants, dates). Column names may differ slightly — use fuzzy matching or inspection
   rather than hardcoded assumptions. If a key column is missing, note it and continue
   with what's available.

2. **Understand the dataset shape** — how many rows? What's the volume distribution?
   A file with 635 emails ranging from 1 send to 245,000 sends needs to be treated very
   differently than a uniform batch. Print a volume distribution (e.g. how many emails
   have Sent < 100, 100–1K, 1K–10K, 10K+).

3. **Immediately tier by volume.** Any email with Sent < 100 is statistically unreliable —
   a single open on a 1-send email = 100% open rate, which is noise not signal. Separate
   these into a "low volume" group early. Never rank, benchmark, or surface these as
   top/bottom performers. The main analysis should only cover emails with Sent ≥ 100.

4. **Look at the data with fresh eyes.** Before classifying anything, scan for patterns:
   - Are there campaign series? (Email 1, Email 2, Email 3 in the same campaign name)
   - Are there A/B test variants? (Subject Line Test, Whole Emails Test, v1/v2, resends)
   - Are there date columns? If so, what time period does the data cover?
   - Are there any rows where the % metrics look impossible or inconsistent?
     (e.g. CTR > Open Rate, or % Delivered > 100%) — flag these as Marketo data anomalies.

5. **Read `references/email-types.md` now.** Classify each email (Sent ≥ 100) into one
   of the defined types using the name pattern rules. Assign the correct benchmark set.

6. Separate into groups:
   - **Standard emails** — main analysis pool
   - **A/B test emails** — set aside for the dedicated A/B section; link variants by
     campaign name for side-by-side comparison
   - **Campaign series** — group Email 1/2/3 etc. together to show funnel drop-off
   - **Low volume** — excluded from all averages

---

## Step 2: Analyze Performance

**Read `references/benchmarks.md` now.**

The goal here is insight, not just averages. Good analysis surfaces things the client
wouldn't have noticed on their own. Think about what the numbers are actually saying.

**Always use volume-weighted metrics for program-level figures.** A simple mean across
635 emails is meaningless — a 245K-send campaign should carry far more weight than a
500-send one. Use: `sum(metric * Sent) / sum(Sent)` for weighted rates.

**For each standard email**, compare against benchmarks for its type and assign traffic
light status (🟢 🟡 🔴) per metric, then derive an overall email status from the
worst single flag.

**Look for these patterns** — surface them explicitly if found:
- Campaign series funnel drop: if Email 2 open rate is <60% of Email 1, that's a
  meaningful drop worth flagging. If Email 3 drops further, note the decay trend.
- High CTR with low open rate: suggests strong content but deliverability or subject
  line problems upstream.
- High open rate with very low CTR: audience is curious but the CTA or content isn't
  converting — different problem than low opens.
- High unsubscribe rate on a specific campaign type: signals audience mismatch, not
  just a bad email.
- Delivery rate below 95% program-wide: masks a deeper list hygiene issue.

**Compute program-level aggregates** (volume-weighted, Sent ≥ 100 only):
- Overall delivery rate
- Weighted open rate (marketing emails only, excluding transactional)
- Weighted CTR
- Weighted unsubscribe rate
- Bounce analysis if bounce columns are present

Assign an **overall program health score** 🟢 / 🟡 / 🔴 based on how the weighted
program metrics compare to the SaaS healthy targets in `references/benchmarks.md`,
and the proportion of emails with critical flags.

---

## Step 3: Build the DOCX Report

**Read `references/report-writing.md` now.** Follow the DOCX structure, tone guidelines,
and template spec defined there precisely.

Use the `docx` npm library (see DOCX skill for full technical reference if needed).

Logo placeholders:
- `assets/mary-logo.png` — Mary's logo (circular, centered on cover page)
- `assets/allgood-logo.png` — allGood logo (centered in footer with "Powered by allGood")
- If either file is missing, leave a clearly labeled placeholder box

Save the output to `/mnt/user-data/outputs/email-performance-report.docx`.

---

## Step 4: Validation Checklist

After generating the DOCX, run through every item below. Fix any failures before delivering.

- [ ] All program-level metrics are volume-weighted, not simple averages
- [ ] Emails with Sent < 100 are excluded from all averages and rankings
- [ ] No email with Sent < 100 appears as a "top" or "bottom" performer
- [ ] Every email in the analysis pool (Sent ≥ 100) has a detected type — no "Unknown" rows
- [ ] Every 🔴 flagged email has a callout stating the specific threshold breached
- [ ] Exec Summary references specific numbers — no vague language like "some emails underperformed"
- [ ] Campaign series (Email 1/2/3) are analyzed as a funnel, not independent rows
- [ ] Action plan has at least one item in each horizon: Immediate, 30-day, 90-day
- [ ] No metric contradicts another (e.g. CTR > OR without an MPP/bot note)
- [ ] Any impossible/inconsistent Marketo data anomalies are flagged explicitly
- [ ] A/B test takeaways are folded into Key Findings bullets (no standalone A/B section)
- [ ] Top 5 worst-performing emails (🔴) are called out in Key Findings with specific metrics
- [ ] Both logos are present or clearly placeholder-labeled
- [ ] Footer on every page shows "Powered by allGood" with allGood logo
- [ ] Cover page shows centered title, subtitle, mary-logo, and allGood branding
- [ ] Report fits within 2-page budget (exec summary + key findings, then action plan)

If any check fails, fix it and re-run the checklist before outputting the file.
