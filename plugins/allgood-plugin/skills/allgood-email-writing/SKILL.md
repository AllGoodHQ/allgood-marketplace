---
name: allgood-email-writing
description: >-
  Write marketing emails that convert — either a single email or a complete
  multi-email sequence — from an offer, an audience, and an optional brand voice.
  Covers welcome, nurture, conversion, launch, re-engagement, and post-purchase
  sequences, and writes every email with direct-response copy principles
  (headlines, curiosity gaps, one CTA, no AI tells). Use when: (1) a user asks
  for a welcome sequence, nurture sequence, drip campaign, email funnel, or
  launch sequence, (2) they want a single marketing, sales, or announcement email
  written or rewritten, (3) they ask to punch up email copy or write subject
  lines that get opened.
---

# allGood — Email Writing

Most marketing email fails the same two ways. The sequence is wrong — a pitch
arrives before any trust was earned, or value emails pile up and never ask for
anything. Or the sequence is right and the writing is dead — corporate hedging,
guru hype, and the smooth, hedged register of an AI that has never wanted
anything.

This skill fixes both. It decides the **architecture** (how many emails, in what
order, on what schedule, each doing one job), then writes the **words** with
direct-response craft, in the brand's voice.

---

## What you need before writing

Four inputs. Three are required, one is optional. Gather them in Step 1 —
do not start drafting without the required three.

| Input | Required | What it is |
|---|---|---|
| **The offer** | Yes | What is eventually being sold, and its price point |
| **The audience** | Yes | Who is receiving this, and where they came from |
| **The goal** | Yes | One sequence type, or one email's single job |
| **Brand voice** | No | A brand voice document — a style/tone guide, or 3+ real sample emails |

**Price point matters more than it looks.** It sets how much trust must be built
before the ask — a $29 impulse buy and a $5,000 program need different sequence
lengths, not just different words. Ask for it if it is missing.

**Brand voice is optional and materially improves the result.** Supply it as a
document: a written style or tone guide, or three-plus real sample emails to
derive the voice from. One-line descriptions ("warm but direct") are a steer,
not a profile. Without any of it the copy is good but generically good — it
sounds like the default voice in Step 2 rather than like the brand.

Offer it once, in Step 1, and move on if the user does not have one. Do not
block on it.

---

## What you get out

For a **sequence** — one markdown file containing:

- A sequence overview: type, goal, email count, send schedule
- Every email in full: send timing, subject line, preview text, stated purpose,
  complete body copy, one CTA, and a P.S. where it earns its place

For a **single email** — the same per-email block, on its own.

Write output to a file the user can use. Default to
`<offer-name>-<sequence-type>.md` in the working directory (e.g.
`cloud-report-welcome.md`). If the user named a path or format, use theirs.

---

## The references

Two reference files. **Load each one at its step, not up front** — the copy
reference alone is long, and reading both before you know the goal wastes the
context you will need for drafting.

| Reference | Load at | Covers |
|---|---|---|
| `references/email-sequences.md` | Step 3 | Sequence types, frameworks, per-email purpose, timing, subject-line formulas |
| `references/direct-response-copy.md` | Step 4 | Headlines, openings, curiosity gaps, flow, CTAs, AI tells to avoid, and the classic reference material |

For a **single email**, skip Step 3 — there is no architecture to decide. Go
straight from voice to copy.

---

## Workflow

### Step 1 — Gather the inputs

Collect the four inputs above. Ask for anything missing among the required
three, in one message rather than one at a time.

For a sequence, also get what `references/email-sequences.md` calls the bridge:
**how the free thing and the paid thing connect.** A welcome sequence off a lead
magnet that has nothing to do with the offer cannot be saved by good writing —
if the bridge does not exist, say so now, not after seven emails.

Then state the plan in two lines and start. Do not run a discovery interview;
the user iterates on a draft far more usefully than on questions.

### Step 2 — Resolve the voice

**If a brand voice document arrived**, read it and compress it to a short
profile you can hold in your head while drafting: register, typical sentence
length, "I" or "we", contractions, humor level, words the brand actually uses,
words it never uses, and how emails open and sign off.

Read sample emails for patterns, not vibes — count things. Are sentences mostly
under 12 words or over 25? Does every email open with a greeting or dive
straight in? Where a style guide and real samples disagree, **the samples win**;
guides state intent, samples show practice.

Show that profile back in a few lines before drafting a full sequence. Getting
voice wrong means rewriting every email rather than editing one, so a
ten-second confirmation is cheaper than a redraft. Skip the confirmation when
the user supplied an explicit style guide you are following as written.

Voice governs **how** things are said. It never overrides what must be said —
sequence structure and persuasion mechanics still apply in full. A formal brand
still gets one CTA per email and still earns the pitch; it just does that
formally. Where they truly collide, voice wins on wording and the mechanics win
on structure: a brand that never uses urgency gets a close email without a
deadline, not no close email.

**If no brand voice document arrived**, write in the voice
`references/direct-response-copy.md` teaches — peer-to-peer, contractions,
short varied sentences, concrete numbers over adjectives, signed with a first
name. **Say in your final response that you used this default**, so the user
knows a voice document would change the result. That default suits founder-led
and B2C brands well and enterprise or regulated brands badly; for those, ask
for a voice document rather than shipping the default and hoping.

### Step 3 — Design the sequence

*Skip for a single email.*

Read `references/email-sequences.md`. Pick the sequence type from the goal, then
decide:

- How many emails, and each one's single job
- The send schedule
- Where the pitch lands, scaled to the price point
- The objection each email handles

Output this as a short plan before drafting — sequence type, email count,
schedule, and a one-line purpose per email. It is much cheaper to fix
architecture here than after the copy exists.

### Step 4 — Write the copy

Read `references/direct-response-copy.md`.

Write each email in full, in the voice from Step 2, doing the one job assigned
in Step 3. Per email: subject line, preview text, body, one CTA.

Three rules that override the temptation to be clever:

- **One CTA per email.** Multiple CTAs means no CTA. The delivery email is the
  one exception — it may carry "download" plus "hit reply."
- **The subject line and preview text are one unit.** The preview continues the
  subject's hook; it never repeats it and never says "having trouble viewing."
- **Specificity is the whole game.** "$47,329 in one day" over "made money."
  Vague claims die on the page — this is the fastest way to make copy sound
  human rather than generated.

The AI tells section of the copy reference is not optional reading. It is the
difference between copy that sounds written and copy that sounds produced.

### Step 5 — Check and write out

Run the finished work against The Test in `references/email-sequences.md` (for a
sequence) and The Test in `references/direct-response-copy.md` (for the writing).
Both are short checklists at the end of those files.

The check that catches the most failures: **does each email do one job, and does
the sequence deliver value before it asks for anything?** If it reads as
"content, content, content, BUY NOW" — the architecture is wrong, and rewriting
the words will not save it.

Then write the output file and tell the user where it is, which sequence type
you used, and whether you were working from their brand voice or the default.
