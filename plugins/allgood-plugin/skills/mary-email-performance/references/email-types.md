# Email Type Classification — Reference
## Name Pattern Rules, Marketo Metric Logic & Campaign Series Analysis

---

## Table of Contents
1. [Email Type Classification Rules](#1-email-type-classification-rules)
2. [Marketo Metric Rules](#2-marketo-metric-rules)
3. [Campaign Series Detection](#3-campaign-series-detection)
4. [A/B Test Detection](#4-ab-test-detection)
5. [Low Volume Handling](#5-low-volume-handling)

---

## 1. Email Type Classification Rules

Classify each email by scanning its Email Name. Apply rules in order — first match wins.
If no pattern matches, assign **Marketing Campaign** as the default.

| Type | Name Patterns to Look For | Benchmark Set |
|---|---|---|
| **Triggered / Auto-Responder** | `Auto-Responder`, `Autoresponder`, `auto-responder`, `triggered`, `trigger` | Triggered |
| **Onboarding / Welcome** | `Onboarding`, `Welcome`, `onboard`, `Getting Started`, `Activation` | Onboarding |
| **Event Follow-Up** | `Follow-up`, `Follow up`, `Visited Booth`, `Post-Event`, `Webinar Follow`, `Demo Follow`, `Conference` | Event Follow-Up |
| **Re-engagement** | `Re-engagement`, `Re-Engagement`, `Win-back`, `Winback`, `Reactivat` | Re-engagement |
| **Nurture / Drip** | `Nurture`, `Drip`, `Sequence`, `Series`, `Track` | Nurture |
| **A/B Test** | `Subject Line Test`, `Whole Emails Test`, `A/B`, `AB Test`, `Variant`, `Version A`, `Version B` | See Section 4 |
| **Resend** | `Resend`, `Re-send`, `Email 2` following an `Email 1` in the same campaign | See Section 3 |
| **Marketing Campaign** | Everything else, or large batch sends (Sent > 5,000) with no other match | Marketing Campaign |

**Coding format in the name:** Many Marketo email names contain bracketed codes like
`[CO/AW/S]`, `[DA/SEM/GO]`. These are campaign taxonomy codes and should be ignored
for type classification. Strip them when displaying the email name in the report.

**Date prefixes:** Names like `2024.05.06 - Whitepaper: ...` or `C.US.25.02 ...` contain
date/region prefixes. These help group campaign series (same campaign = same base name
after the prefix). Strip date/region prefixes for display but use them for series grouping.

---

## 2. Marketo Metric Rules

Marketo applies these rules when building the Email Performance Report. Use them to
validate whether reported figures are internally consistent, and to flag anomalies.

**Rule 1:** Each email activity is counted as exactly one of: Delivered, Hard Bounced,
Soft Bounced, or Pending. These four should sum to Sent.

**Rule 2:** If an email shows Opened, it is counted as Delivered.

**Rule 3:** If an email shows Clicked or Unsubscribed, it is counted as both
Delivered AND Opened. This means:
- Opened ≥ Clicked (always — you can't click without opening)
- Opened ≥ Unsubscribed (always)
- If the data shows Clicked > Opened, this is a Marketo data anomaly — flag it

**Rule 4:** If Opened, bounces are ignored. If not opened, Hard Bounce takes
precedence over Soft Bounce.

**Rule 5:** If no email activity is received within 3 days of send, it is deemed Aborted.
High Abort numbers indicate delivery problems — the email left Marketo but never
generated a bounce or open response from the receiving server.

**Data consistency checks to run:**
- Delivered + Hard Bounced + Soft Bounced + Pending should ≈ Sent (allow small rounding)
- % Opened = Opened / Delivered (not Opened / Sent)
- % Clicked = Clicked / Delivered (not Clicked / Opened — that's CTOR)
- Flag any row where these don't reconcile within 1%
- Flag any row where Abort is unusually high relative to Sent (> 5%)

---

## 3. Campaign Series Detection

Campaign series are multiple emails sent sequentially as part of the same campaign.
They should be analyzed as a funnel, not as independent sends.

**How to detect series:**
- Same campaign base name with sequential Email 1, Email 2, Email 3 suffixes
- Example: `C.US.22.12.16_Visitors_Expansion.Email 1 v2`, `...Email 2 v2`, `...Email 3 v2`
- Look for `.Email #`, `.Email 1`, `.E1`, `Step 1`, `Step 2` patterns

**How to analyze series:**
- Open rate decay: Email 2 OR < 80% of Email 1 OR = normal; < 60% = flag
- Click rate decay: some decay is normal as disengaged readers drop off; steep drop signals content problem
- Unsubscribe spike at a specific email in the series: that email's content or
  frequency is the likely cause
- If the series has a Resend (e.g. "Email 2 (Resend of Email 1)"), compare the
  resend's OR and CTR to the original send — a good resend should achieve 40–60%
  of the original engagement from the remaining non-openers

**In the report:** Group series together in the Campaign Type section with a mini
funnel table (Email 1 → Email 2 → Email 3) showing the progression. Do not list
them as separate independent rows in the main per-email table.

---

## 4. A/B Test Detection

A/B tests contain variants of the same email and should never be benchmarked as
independent emails — their performance only makes sense relative to each other.

**How to detect:**
- Name contains: `Subject Line Test`, `Whole Emails Test`, `Test`, `v1`/`v2`/`v3`,
  `Variant A`/`B`, `Version A`/`B`
- Multiple emails with the same campaign base name but different subject/content indicators
- A "Resend" email that immediately follows a large campaign send is often effectively
  an A/B test of subject line to non-openers — treat it as such

**How to analyze A/B tests:**
- Group all variants together by campaign
- Compare: Open Rate, CTR, CTOR, Unsubscribe Rate across variants
- Declare a winner based on the primary metric relevant to the test type:
  - Subject line test → winner by Open Rate
  - Full email / content test → winner by CTR or CTOR
  - If Sent volumes differ significantly between variants (> 20% imbalance),
    note this as it affects statistical confidence
- If combined Sent across variants < 500, flag as "insufficient volume for
  statistical confidence — directional only"

**In the report:** These appear ONLY in the dedicated A/B Test section.
Remove them from the main per-email breakdown table entirely.

---

## 5. Low Volume Handling

Any email with Sent < 100 is statistically unreliable for performance benchmarking.

- Do not include in any program-level averages or weighted metrics
- Do not rank as top or bottom performer
- Do not apply traffic-light benchmarking
- Do list them in an appendix table with a standard note:
  "Low volume (< 100 sends) — metrics not statistically significant"
- Exception: if a low-volume email has an unusually high Abort or Bounce count
  (e.g. 3 hard bounces on 7 sends = 43% bounce rate), this IS worth flagging
  as a data quality signal even though volume is low
