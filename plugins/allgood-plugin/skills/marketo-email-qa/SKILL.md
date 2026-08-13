---
name: marketo-email-qa
description: >
  Use this skill whenever a user wants to QA, test, proof, or pre-flight a
  Marketo email before sending it. Triggers include: "QA this email",
  "test email 1234", "is this email ready to send", "check my email before I
  send", "pre-flight this email", "are the links in this email working",
  "check the UTMs on this email", "did I break any tokens", "proof this email",
  "run QA on the webinar invite", or any request to review a Marketo email for
  broken links, missing UTMs, unresolved {{my.Tokens}}, missing alt text,
  typos, or compliance gaps like a missing unsubscribe link. Also use it when
  a user names a Marketo email and asks whether it looks right. Always use
  this skill even if the user just says "check this email" — if it's a Marketo
  email and they want it looked over before it goes out, this skill applies.
---

# Marketo Email Pre-Flight QA

## User Request

The user has requested: $ARGUMENTS

Adapt to what they asked for:

- **A specific concern named** ("are the links working?", "check the UTMs") → run the full check, but
  lead the report with that concern and keep the rest brief.
- **"Quick check" or "just the blockers"** → skip the full report. Reply in chat with the overall
  assessment, every 🔴, and nothing else.
- **A generic ask** ("QA this email", "is it ready?") → the full report, all steps.
- **No email identified** → resolve it first (Step 1). Never guess at an email ID.

## How this skill works

Three layers, and keeping them separate is what makes the output trustworthy:

1. **`marketo_test_email` measures.** It resolves every link through its redirects, reads UTMs off the
   final URLs, records image attributes, extracts token references, and returns the visible copy. It
   assigns **no severities** — that is deliberate.
2. **`references/qa-policy.md` decides.** It maps that data to 🔴/🟡/🟢. It is allGood's default and the
   user can override it.
3. **You judge what code can't** — grammar, tone, placeholder copy, whether a button's label matches
   where it actually goes — then write the report.

Two things follow from this that you must not do:

- **Never invent a severity.** Every flag traces to a rule in the policy file.
- **Never re-litigate a measurement.** If the tool reports a 404, don't re-fetch the URL, don't hedge,
  don't speculate that it might work for recipients. It returned 404.

## Reference Files

| File | Load when |
|---|---|
| `references/mcp-tools.md` | Before calling the tool, or if it isn't available |
| `references/qa-policy.md` | Step 3, before assigning any severity |
| `references/report-format.md` | Step 5, before writing the report |

Load them at the step that needs them — not all at once.

## Step 1: Identify the email

If the user gave a numeric email ID, use it.

If they named an email or campaign instead:

```
marketo_get_programs_by_name(name="<what they said>")
```

Then find the email inside the matching program. If more than one email could be meant, **list the
candidates and ask** — QA-ing the wrong email is worse than a slow question.

If nothing matches, say so and ask for the email ID directly.

## Step 2: Collect the measurements

**Read `references/mcp-tools.md` now** if you haven't. It documents the response shape and the fields
that are easy to misread.

```
marketo_test_email(emailId=<id>)
```

This fetches every link and image, so it takes a few seconds on a link-heavy email. Only pass
`checkLinks=false` if the user explicitly wants a fast offline pass — and if you do, say in the report
that no URL was verified.

Capture from the response:

- `checksSkipped` — anything here must appear in the report.
- `email.previewUrl` — link it at the end.
- `bodyText` — this is what you'll read in Step 4.

If the tool comes back as plain text rather than JSON, it failed. See the error table in
`references/mcp-tools.md`.

## Step 3: Apply the policy

**Read `references/qa-policy.md` now.** Also check the working directory for
`.allgood/email-qa-policy.md` — if it exists, it overrides the defaults for any rule it mentions.

Walk each section against the data and collect findings. Four traps, in the order people fall into them:

1. **`{{lead.*}}` and `{{system.*}}` are never defects.** They're unresolved in the asset *by design*
   and Marketo fills them in per recipient. `tokens.literalInSendingHtml` splits by namespace precisely
   so you can tell. Flagging them fires on nearly every personalised email and is the fastest way to
   make this report worthless.
2. **`alt=""` is correct**, not missing alt text. Only `alt: null` is a finding.
3. **Skip `likelyTrackingPixel` images.** They're analytics beacons, not design.
4. **Judge `finalUrl`, never the click-tracker.** A Marketo tracking domain mid-chain is normal.

## Step 4: Judge the copy

This is the half no amount of code can do. Read `bodyText` and apply the `CPY-*` rules from the policy.

The one worth real attention: **does every link's label match where it goes?** Compare each
`links[].text` against its `check.finalUrl`. "Register for the webinar" pointing at a pricing page
passes every automated check and is exactly the mistake that embarrasses someone. This is why the tool
returns both fields.

Also check whether alt text describes *this* email — alt text left over from last month's newsletter is
a common and easily-missed error.

Don't flag: text inside HTML comments, typos in image filenames, deliberate lowercase branding, or
sentence fragments used for rhythm.

## Step 5: Write the report

**Read `references/report-format.md` now.** Follow its structure exactly — it matches allGood's public
email-testing tool, so marketers recognise it.

Consolidate before you classify. Four separate "missing UTM" findings are **one** finding listing four
links. This step is the difference between a report someone reads and a report someone closes.

## Step 6: Offer the fix

If you found token problems and the user has token-write access, offer to fix them:

> Three tokens need attention. Want me to update them? `my.Headline` is undefined —
> I'd add it with the value from the subject line.

Use the `marketo-tokens` skill for the actual edits; it has the safety gates for writing to a live
program. **Never write to a program without explicit confirmation.**

For broken links, missing alt text, and copy fixes, tell them what to change — those live in the email
editor, not in tokens.

## Validation Checklist

Before delivering:

- [ ] Every flag traces to a rule in `qa-policy.md` — none invented
- [ ] No rule IDs (`MET-07`, `TOK-04`) appear in the output
- [ ] No `{{lead.*}}` or `{{system.*}}` token is flagged as a problem
- [ ] Related findings are consolidated, not listed one per rule
- [ ] `overall_risk` follows worst-flag-wins
- [ ] Every `checksSkipped` entry is stated in the report
- [ ] Counts in `## Summary` match the items actually listed below
- [ ] Empty sections are omitted
- [ ] Findings name the specific link, image, token, or number — no vague "some links"
- [ ] Passed Checks reads as reassuring, not as a checklist
- [ ] `previewUrl` is linked, when the tool returned one
- [ ] No measurement was re-fetched or second-guessed

If any check fails, fix it and re-run the checklist before delivering.
