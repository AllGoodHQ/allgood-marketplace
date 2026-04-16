# Health Check Rules

Run every rule below against the collected program data. Each rule has an ID, severity
level, detection condition, message template, and a recommendation.

---

## Severity Levels

| Level | Meaning | Color |
|---|---|---|
| **Critical** | Blocks program from running correctly or indicates a broken state | Red `#DC3545` |
| **Warning** | Program will run but quality or completeness is compromised | Orange `#F39C12` |
| **Info** | Best-practice suggestion — not a functional issue | Blue `#4A90D9` |

---

## Detection Rules

### HC-01: No Description

| Property | Value |
|---|---|
| Severity | Warning |
| Condition | `program.description` is null or empty AND `program.status` is not "Draft" |
| Message | "Active program has no description — purpose is undocumented" |
| Recommendation | "Add a 1-2 sentence description explaining what this program does and who owns it" |

### HC-02: Missing Tags

| Property | Value |
|---|---|
| Severity | Warning |
| Condition | `program.tags` is empty or not present |
| Message | "No tags assigned to program" |
| Recommendation | "Add tags (Region, Product Line, Business Unit, Campaign Type) — these drive downstream reporting in Revenue Explorer and Program Analyzer" |

### HC-03: No Period Cost

| Property | Value |
|---|---|
| Severity | Warning |
| Condition | `program.costs` is empty AND `program.status` is not "Draft" |
| Message | "No period cost defined for [type] program" |
| Recommendation | "Add a period cost (even $0) — required for ROI calculations (Cost per Success, Cost per New Name)" |

### HC-04: Potentially Idle Trigger Campaign

| Property | Value |
|---|---|
| Severity | Info |
| Condition | Smart campaign type is "trigger" AND status is "Active" AND program `createdAt` is more than 90 days ago |
| Message | "Trigger campaign '[name]' is active — created [date]. Verify it is still needed" |
| Recommendation | "Review whether this trigger is still serving its purpose. Marketo flags idle triggers via Campaign Cleanup notifications — check if this has been flagged" |

Note: This is heuristic — we cannot see actual activity timestamps via this API path.
The flag is informational, not conclusive.

### HC-05: Placeholder Token Values

| Property | Value |
|---|---|
| Severity | Warning |
| Condition | Token value matches any placeholder pattern (see Placeholder Detection below) |
| Message | "Token '[name]' has placeholder value: '[value snippet]'" |
| Recommendation | "Update with actual content before launching — placeholder values will render in live emails" |

### HC-06: Draft Assets in Active Program

| Property | Value |
|---|---|
| Severity | Critical |
| Condition | `program.status` is not "Draft" AND any email or landing page has status "Draft" or "Unapproved" |
| Message | "Draft [asset type] '[name]' found in active program" |
| Recommendation | "Approve the asset or deactivate the program. Draft emails/LPs will not render if referenced by a live smart campaign" |

### HC-07: Empty Token Values

| Property | Value |
|---|---|
| Severity | Warning |
| Condition | Token value is null, empty string, or whitespace-only |
| Message | "Token '[name]' ([type]) has no value defined" |
| Recommendation | "Set a value or confirm this token is intentionally empty (inherited value may apply)" |

### HC-08: Naming Convention

| Property | Value |
|---|---|
| Severity | Info |
| Condition | Program name does not follow a recognizable naming convention (no date prefix, no channel indicator, or inconsistent pattern) |
| Message | "Program name may not follow team naming convention" |
| Recommendation | "Consider standardizing to a convention like 'YYYY-MM_Channel_CampaignName' for easier filtering and search at scale" |

Note: Naming conventions vary by organization. This is a soft suggestion, not a hard rule.

### HC-09: No Smart Campaigns

| Property | Value |
|---|---|
| Severity | Warning |
| Condition | Program has zero smart campaigns |
| Message | "Program has no smart campaigns" |
| Recommendation | "Without smart campaigns, this program cannot process leads automatically. Add campaigns or verify this is intentional (e.g., used for tokens/assets only)" |

### HC-10: No Emails in Email-Type Program

| Property | Value |
|---|---|
| Severity | Info |
| Condition | `program.type` is "Email" or "Engagement" AND no email assets found |
| Message | "No email assets in [type] program" |
| Recommendation | "This program type typically includes emails. Add email assets or verify the program type is correct" |

### HC-11: All Campaigns Inactive

| Property | Value |
|---|---|
| Severity | Warning |
| Condition | Program has 1+ smart campaigns AND none are Active |
| Message | "All [N] smart campaigns are inactive" |
| Recommendation | "If this program is supposed to be running, activate the relevant campaigns. If it's been sunset, consider archiving the program" |

### HC-12: No Local Token Overrides

| Property | Value |
|---|---|
| Severity | Info |
| Condition | `get_tokens_by_folder` returns empty (no local tokens) but emails in the program reference `{{my.*}}` tokens |
| Message | "Program uses only inherited tokens — no local overrides" |
| Recommendation | "Inherited tokens may work fine, but if this program needs unique values, create local tokens to override the inherited defaults" |

Note: Detection of token references in emails requires scanning email content sections
for `{{my.*}}` patterns.

### HC-13: Empty Smart List

| Property | Value |
|---|---|
| Severity | Warning |
| Condition | Smart campaign's smart list has zero rules (no triggers and no filters) |
| Message | "Smart campaign '[name]' has an empty smart list — no filters or triggers defined" |
| Recommendation | "A campaign with no qualification criteria cannot process leads. Add triggers (for real-time) or filters (for batch) to define who enters" |

### HC-14: No Flow Steps

| Property | Value |
|---|---|
| Severity | Warning |
| Condition | Smart campaign has zero flow steps |
| Message | "Smart campaign '[name]' has no flow steps — it does nothing when triggered" |
| Recommendation | "Add flow steps to define what happens when a lead qualifies (send email, change status, update field, etc.)" |

### HC-15: Qualification Set to Once

| Property | Value |
|---|---|
| Severity | Info |
| Condition | Smart campaign qualification is set to "once" (person can only run through once) |
| Message | "Campaign '[name]' qualification is set to 'once' — leads can only enter once" |
| Recommendation | "This is often correct (e.g., welcome campaigns). But if leads should re-qualify (e.g., event RSVPs, recurring nurtures), consider changing to 'every time' or 'once every N days'" |

---

## Placeholder Detection Patterns

When checking token values (HC-05), test against these patterns. A match on any pattern
means the value is likely a placeholder.

```
Pattern                                          Example matches
─────────────────────────────────────────────────────────────────
/^(enter|add|update|replace|insert|put)\s/i      "Enter your subject line here"
/^(TBD|TODO|TBC|N\/A|NA|XXX|PLACEHOLDER)$/i      "TBD", "TODO", "PLACEHOLDER"
/^https?:\/\/(example\.com|placeholder)/i         "https://example.com/page"
/^\{\{.*\}\}$/                                    "{{my.SubjectLine}}" (self-ref)
/^(Lorem ipsum|test|sample)\s/i                   "Lorem ipsum dolor sit amet"
/^(your |my |the |a )?(text|copy|content|url|link|image|value)\s*(here)?$/i
                                                  "Your text here", "content here"
/^\[.*\]$/                                        "[Subject Line]", "[Enter URL]"
/^<.*>$/                                          "<your headline>"
```

If a token value is very short (under 3 characters) and is not a number or date type,
also flag it as potentially incomplete — but at Info severity, not Warning.

---

## Grouping Multiple Flags

If the same rule fires for multiple assets (e.g., HC-06 fires for 3 draft emails),
group them into a single finding:

**Message:** "3 draft emails found in active program: [Email A], [Email B], [Email C]"

This prevents the health flag table from becoming excessively long for programs with
many issues of the same type.

---

## Output Format

Produce findings as a structured list sorted by severity (Critical first):

```
[
  {
    id: "HC-06",
    severity: "Critical",
    flag: "Draft email in active program",
    details: "Email 'Webinar Invite v2' is in Draft status",
    recommendation: "Approve the email before campaign launch"
  },
  ...
]
```

Map each finding to a row in the Health Flag Table (Type D in document-format.md).
