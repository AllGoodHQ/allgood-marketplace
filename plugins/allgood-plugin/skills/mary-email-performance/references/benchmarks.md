# Email Performance Benchmarks — Canonical Reference
## SaaS / Technology, 2025–2026

This is the single source of truth for all benchmark comparisons in the report.
Do not blend figures from different sources. Use these numbers for all flagging and
traffic-light assignments.

---

## Table of Contents
1. [Traffic Light Thresholds — All Email Types](#1-traffic-light-thresholds)
2. [SaaS-Specific Healthy Targets](#2-saas-healthy-targets)
3. [Benchmarks by Email Type](#3-benchmarks-by-email-type)
4. [Program-Level Health Scoring](#4-program-level-health-scoring)
5. [Key Context Notes](#5-key-context-notes)

---

## 1. Traffic Light Thresholds

Use these to assign 🟢 / 🟡 / 🔴 to each metric for each email.
The "email type" benchmarks in Section 3 override these defaults where specified.

| Metric | 🟢 Healthy | 🟡 Caution | 🔴 Action Required |
|---|---|---|---|
| Delivery Rate | ≥ 97% | 94–96.9% | < 94% |
| Open Rate (marketing) | ≥ 25% | 15–24.9% | < 15% |
| Open Rate (transactional/triggered) | ≥ 50% | 35–49.9% | < 35% |
| CTR (marketing) | ≥ 2% | 1–1.9% | < 1% |
| CTR (transactional/triggered) | ≥ 5% | 2–4.9% | < 2% |
| Click-to-Open Rate | ≥ 10% | 5–9.9% | < 5% |
| Unsubscribe Rate | < 0.2% | 0.2–0.5% | > 0.5% |
| Hard Bounce Rate | < 0.5% | 0.5–1% | > 1% |
| Soft Bounce Rate | < 1% | 1–2% | > 2% |

**Critical overrides — these always trigger 🔴 regardless of type:**
- Unsubscribe rate > 1% on any single send = immediate flag
- Delivery rate < 90% = critical deliverability issue
- Any email where CTR > Open Rate = data anomaly, flag separately

---

## 2. SaaS Healthy Targets

These are the program-level targets to compare against in the Benchmarks Comparison
section of the report. These represent what a well-run SaaS email program should achieve.

| Metric | SaaS Industry Avg | Healthy Target | Notes |
|---|---|---|---|
| Open Rate (marketing) | 19–25% | 25–35% | MPP distorts; use as directional only |
| CTR (marketing) | 1.2–1.9% | 2–2.5% | Most reliable cross-source metric |
| CTR (triggered/automated) | 2–3% | 3.8%+ | Triggered emails outperform campaigns |
| Click-to-Open Rate | 8–12% | 10–15% | Better signal than open rate alone |
| Unsubscribe Rate | 0.1–0.2% | < 0.15% | Per send; not cumulative |
| Delivery Rate | 94–97% | > 98% | Below 95% = investigate immediately |
| Inbox Placement Rate | ~80.9% | > 85% | Requires 3rd-party tool to measure |

**Important:** SaaS sits at the bottom of inbox placement at ~80.9% industry average.
Nearly 1 in 5 SaaS marketing emails misses the inbox entirely. A delivery rate that
looks fine in Marketo can mask significant spam folder placement.

---

## 3. Benchmarks by Email Type

Each email type has its own benchmark set. Always use the type-specific targets,
not the generic SaaS averages, when flagging individual emails.

### Marketing Campaigns (mass sends, newsletters, product announcements)
| Metric | Healthy | Caution | Action Required |
|---|---|---|---|
| Open Rate | ≥ 22% | 12–21.9% | < 12% |
| CTR | ≥ 1.5% | 0.8–1.4% | < 0.8% |
| CTOR | ≥ 8% | 4–7.9% | < 4% |
| Unsubscribe | < 0.2% | 0.2–0.4% | > 0.4% |
| Delivery Rate | ≥ 97% | 94–96.9% | < 94% |

### Triggered / Auto-Responders (behavior-triggered, automated)
| Metric | Healthy | Caution | Action Required |
|---|---|---|---|
| Open Rate | ≥ 50% | 35–49.9% | < 35% |
| CTR | ≥ 5% | 2–4.9% | < 2% |
| CTOR | ≥ 15% | 8–14.9% | < 8% |
| Unsubscribe | < 0.1% | 0.1–0.3% | > 0.3% |
| Delivery Rate | ≥ 99% | 97–98.9% | < 97% |

*Note: Triggered emails should always outperform campaigns. If they don't,
that's a content or relevance problem, not a list problem.*

### Onboarding / Welcome Sequences
| Metric | Healthy | Caution | Action Required |
|---|---|---|---|
| Open Rate | ≥ 50% | 35–49.9% | < 35% |
| CTR | ≥ 4% | 2–3.9% | < 2% |
| CTOR | ≥ 12% | 6–11.9% | < 6% |
| Unsubscribe | < 0.15% | 0.15–0.4% | > 0.4% |
| Delivery Rate | ≥ 99% | 97–98.9% | < 97% |

*Welcome Email 1 should be the highest-performing email in the entire program.
Below 40% open rate on Email 1 = deliverability or expectation mismatch issue.*

### Event Follow-Up (conference, webinar, demo follow-up)
| Metric | Healthy | Caution | Action Required |
|---|---|---|---|
| Open Rate | ≥ 35% | 20–34.9% | < 20% |
| CTR | ≥ 5% | 2–4.9% | < 2% |
| CTOR | ≥ 15% | 8–14.9% | < 8% |
| Unsubscribe | < 0.3% | 0.3–0.8% | > 0.8% |

*Event follow-ups have context-driven urgency; high unsubscribes can indicate
the event list was added without clear consent.*

### Re-engagement Campaigns
| Metric | Healthy | Caution | Action Required |
|---|---|---|---|
| Open Rate | ≥ 10% | 5–9.9% | < 5% |
| CTR | ≥ 1% | 0.5–0.9% | < 0.5% |
| Unsubscribe | < 2% | 2–4% | > 4% |

*Re-engagement campaigns inherently produce higher unsubscribes (0.5–2% is expected
and desirable — it cleans the list). Below 5% open rate = audience is unreachable,
suppress them.*

### Nurture / Drip Sequences (multi-email content series)
| Metric | Healthy | Caution | Action Required |
|---|---|---|---|
| Open Rate | ≥ 20% | 12–19.9% | < 12% |
| CTR | ≥ 2% | 1–1.9% | < 1% |
| CTOR | ≥ 10% | 5–9.9% | < 5% |
| Unsubscribe | < 0.3% | 0.3–0.6% | > 0.6% |

---

## 4. Program-Level Health Scoring

After computing volume-weighted program metrics, assign an overall health score:

**🟢 Healthy Program**
- Delivery rate ≥ 96%
- Weighted open rate ≥ 20%
- Weighted CTR ≥ 1.5%
- Unsubscribe rate < 0.25%
- < 15% of emails (by volume) have a 🔴 flag

**🟡 Caution**
- Any one metric in the Caution range, OR
- 15–30% of emails (by volume) have a 🔴 flag

**🔴 Action Required**
- Delivery rate < 94%, OR
- Weighted CTR < 1%, OR
- Unsubscribe rate > 0.5%, OR
- > 30% of emails (by volume) have a 🔴 flag

---

## 5. Key Context Notes

**On open rates:** Apple Mail Privacy Protection (MPP) pre-fetches tracking pixels,
inflating open rates for the ~49% of email opens that come through Apple Mail.
Open rate trends over time are more meaningful than absolute numbers. When open rate
is high but CTR is low, suspect MPP inflation before assuming engagement.

**On CTR as primary metric:** CTR is the most reliable cross-source comparison metric
and should be the anchor KPI for any performance narrative. It requires a human to
actually click, making it far less susceptible to bot/proxy inflation than open rate.

**On bounce rate and delivery rate:** Marketo's delivery rate = accepted by receiving
server. It does NOT measure inbox placement. A 97% delivery rate can still mean 20%
of emails go to spam. The delivery rate in this report is a floor, not a ceiling.

**On unsubscribe rate:** A high unsubscribe rate on a large send is a different
severity than the same rate on a small send. Flag the absolute unsubscribe count
alongside the percentage when significant.

**On bot clicks:** In B2B environments, corporate security tools click every link
automatically. Up to 40% of recorded clicks may be bots. High CTR with zero or
very low downstream conversions (or unusually fast click times) suggests bot inflation.
Note this as a caveat whenever CTR looks unexpectedly strong.
