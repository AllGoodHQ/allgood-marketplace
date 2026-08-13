# Email QA Report Format

> Loaded by `marketo-email-qa/SKILL.md` when it is ready to write the report.

This is the same format allGood's public email-testing tool produces, so a marketer who has used the
free tool sees output they already recognise. Follow it exactly.

## Table of contents

- [Consolidate before you classify](#consolidate-before-you-classify)
- [Overall risk](#overall-risk)
- [The report structure](#the-report-structure)
- [Headline rules](#headline-rules)
- [Voice](#voice)
- [Phrasing table](#phrasing-table)

## Consolidate before you classify

**This is the step most likely to be skipped, and skipping it is what makes a report unreadable.**
Before writing anything, merge related findings into single marketer-facing items. Never list
near-identical findings separately.

Wrong:

```
🟡 Header logo lacks UTM parameters
🟡 Hero image link lacks UTM parameters
🟡 Main CTA lacks UTM parameters
🟡 Footer link lacks UTM parameters
```

Right:

```
🟡 **Four links need UTM parameters** — header logo, hero image, main CTA, and the footer
   "Learn more" link. Without them these clicks won't attribute to this campaign.
```

Apply the same merge to:

| Findings | Consolidate into |
|---|---|
| Several missing UTMs | One item listing every affected link |
| Several images missing alt text | One item with a short list of the images |
| Several broken links | One "multiple broken links" item, each named |
| Several missing metadata fields | One item naming all the missing fields |
| Several undefined tokens | One item listing them, with typo suggestions inline |

The rule: **if findings share a root cause, they are one item.** If they differ only by which element
they landed on, list the elements inside one bullet. The report should read like advice from a
colleague who reviewed the email, not a dump of every rule that fired.

## Overall risk

Count consolidated findings, then:

| Risk | Condition |
|---|---|
| `do_not_send` | One or more 🔴 |
| `needs_attention` | No 🔴, at least one 🟡 |
| `safe` | Neither |

Worst flag wins. One 🔴 among thirty 🟢 is still `do_not_send`.

## The report structure

Use this exact skeleton. Omit any section that would be empty.

```markdown
# Email QA Report for: [Subject Line]

## Overall Assessment: [Safe to Send | Needs Attention | Do Not Send]

## Summary

- 🔴 Critical Issues: Z problems
- 🟡 Recommendations: Y advisories
- 🟢 Passed Checks: X confirmations

## Critical Issues

[Consolidated 🔴 items, grouped by topic]

## Recommendations

[Consolidated 🟡 items]

## Passed Checks

[Friendly, marketer-facing confirmations of what looks right]

---
QA performed at: [ISO 8601 timestamp]
```

Fallback lines when a section is thin but worth keeping:

- No 🔴 → "No critical blockers found."
- No 🟡 → "No additional updates suggested at this time."
- No 🟢 → omit the whole section.

### Two additions to the original format

**Say what didn't run.** If `checksSkipped` from the tool is non-empty, add a short note directly under
`## Summary`:

```markdown
> **Not checked:** token references, because the program that owns this email's My Tokens
> could not be resolved. Everything else below ran normally.
```

A check that could not run must never read as a check that passed. The original tool had no equivalent
because a forwarded email either arrived or didn't; reading a live asset has more ways to come up
partial.

**Link the preview.** When `email.previewUrl` is set, put it at the end so a human can eyeball the
email themselves:

```markdown
[Preview this email in Marketo](<previewUrl>)
```

## Headline rules

If you are sending or titling the report, the headline follows the risk:

| Risk | Headline |
|---|---|
| `safe` | `✅ Email Passed QA: [Subject Line]` |
| `needs_attention` | `⚠️ Email Needs Minor Updates: [Subject Line]` |
| `do_not_send` | `🔴 Email Has Critical Issues: [Subject Line]` |

Use the email's real subject line, not the email's internal asset name.

## Voice

Supportive QA feedback from a colleague. Not a system readout.

- **Plain English, always.** "Broken URL in the main CTA", not "LNK-01 fired on anchor[3]".
- **Never show rule IDs.** `MET-07` and `TOK-04` are for this skill's bookkeeping. A marketer should
  never see them.
- **Be specific.** Name the link, quote the copy, give the number. "Subject line is 168 characters"
  beats "subject line is too long".
- **Passed Checks should feel reassuring**, not like a checklist being read aloud. This section is why
  the report builds confidence rather than anxiety.
- **Red flags are opportunities, not crises.** Say what to do, not just what's wrong.
- **Never invent a severity.** Every flag traces to a rule in `qa-policy.md`. If something bothers you
  that the policy doesn't cover, mention it in prose under Recommendations rather than inventing a
  flag for it.
- **Never re-litigate a measurement.** If the tool says a link returned 404, it returned 404. Don't
  re-fetch it, don't hedge about it, and don't speculate that it might work for recipients.

## Phrasing table

| Instead of | Write |
|---|---|
| "Link works correctly" | "All links are working as expected." |
| "No placeholder text found" | "Copy looks clean and professional." |
| "Metadata fields validated" | "Sender info, subject, and preheader look ready for the inbox." |
| "utm_medium mismatch detected" | "The main CTA is tagged `utm_medium=social` — clicks from this email will report as social traffic." |
| "Token undefined" | "`{{my.Headline}}` isn't defined in this program, so recipients will see the raw token text." |
| "Alt attribute absent on img[2]" | "The hero image is missing alt text." |
| "All image URLs returned 2xx" | "Images render correctly and look sharp." |
| "Copy analysis passed" | "Copy reads smoothly with no grammar or spelling issues." |
| "No critical findings" | "This email looks polished and ready to send!" |
