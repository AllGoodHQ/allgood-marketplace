# Email QA Policy — allGood Defaults

> Loaded by `marketo-email-qa/SKILL.md` to turn `marketo_test_email` measurements into 🔴/🟡/🟢 flags.

**This file is the only place a severity is written down.** `marketo_test_email` returns pure data —
link statuses, UTM parameters, image attributes, token facts, compliance element presence. It assigns
no severities on purpose, because what blocks a send differs per company. Everything below is
allGood's default reading of that data.

## Overriding this policy

These are defaults, not rules. Override them in either of two ways:

1. **Per user** — edit this file in your copy of the skill. It is plain markdown.
2. **Per project** — drop a `.allgood/email-qa-policy.md` file in the working directory. If one
   exists, **read it and let it win** for any rule it mentions; fall back to this file for the rest.
   A project file need only list the rules it changes.

Common overrides worth knowing about:

- Companies that treat attribution as sacred often raise **UTM-01** (`utm_medium` not `email`) to 🔴.
- Companies outside CAN-SPAM's reach sometimes drop **CMP-03** (mailing address) to 🟢.
- Agencies QA-ing client sends often raise **IMG-02** (missing alt text) to 🔴 for accessibility
  compliance.

## Severity meanings

| | Name | Means |
|---|---|---|
| 🔴 | Critical | Do not send until this is fixed. A recipient would see something broken. |
| 🟡 | Recommendation | Send if you're in a hurry, but somebody should look. |
| 🟢 | Passed | Confirmed correct. These are what make the report reassuring rather than a nag list. |

**Spend 🔴 carefully.** A red says "stop the send". Fire it on something that turns out to be fine and
the marketer learns to skip reds — which costs you the reliable ones. Every 🔴 below is a check with a
low false-positive rate. Heuristics get 🟡.

## Metadata — from `email.*`

| ID | Condition | Default | Message |
|---|---|---|---|
| MET-01 | `subject` null or empty after trimming | 🔴 | Subject line is missing |
| MET-02 | `fromName` null or empty | 🔴 | From name is missing |
| MET-03 | `fromEmail` null or empty | 🔴 | From address is missing |
| MET-04 | `fromEmailIsValidFormat` is false | 🔴 | From address is not a valid email address |
| MET-05 | `replyEmailIsValidFormat` is false | 🔴 | Reply-to address is present but not valid |
| MET-06 | `replyEmailIsValidFormat` is null (absent) | 🟡 | No reply-to set; most ESPs fall back to the from address |
| MET-07 | `preHeader` null or empty | 🟡 | No preview text — inboxes will show the first line of body copy instead |
| MET-08 | `subjectLength` < 3 or > 150 | 🟡 | Subject line is very short / very long |
| MET-09 | `preHeaderLength` < 5 or > 180 | 🟡 | Preview text is very short / very long |
| MET-10 | `preHeaderEqualsSubject` is true | 🟡 | Preview text repeats the subject line, wasting the slot |
| MET-11 | Subject is entirely placeholder wording (`test`, `sample`, `placeholder`, `lorem ipsum`, `dummy`, `TBD`) | 🟡 | Subject line still looks like a placeholder |
| MET-12 | Subject is ALL CAPS and not obviously deliberate | 🟡 | All-caps subject lines trip spam filters |
| MET-13 | All of MET-01 through MET-07 pass | 🟢 | `🟢 From, subject, reply-to, and preheader are correctly structured.` |

## Links — from `links[].check`

Skip any link where `hiddenByInlineStyle` is true unless it also has clear CTA text.

| ID | Condition | Default | Message |
|---|---|---|---|
| LNK-01 | `check.ok` is false and `check.statusCode` is 400–599 | 🔴 | Broken link — returns HTTP {statusCode} |
| LNK-02 | `check.error` is set (DNS, TLS, timeout) | 🔴 | Link could not be reached |
| LNK-03 | `check.skipped` is `"private-host"` | 🟡 | Link points at localhost or an internal address, which no recipient can open |
| LNK-04 | `check.skipped` is `"malformed"` | 🔴 | Link is not a valid URL |
| LNK-05 | `check.finalUrl` host matches `staging`/`dev`/`qa`/`preview`/`test.` | 🟡 | Link points at a non-production environment |
| LNK-06 | `check.redirectCount` > 3 | 🟡 | Link goes through {n} redirects before landing |
| LNK-07 | Every checked link has `ok: true` | 🟢 | `All links are working.` |

Never report an intermediate redirect host as a problem. Judge `finalUrl` only — a Marketo
click-tracking domain in the chain is normal and correct.

## UTMs — from `links[].check.utm`

**Only applies to** `scheme` of `http`/`https`. **Exempt entirely:** `mailto:`, `tel:`, any link where
`isUnsubscribe` or `isPrivacyPolicy` is true.

| ID | Condition | Default | Message |
|---|---|---|---|
| UTM-01 | `utm.medium` is set but not `email` | 🟡 | `utm_medium` is `{value}`, not `email` — attribution will land in the wrong channel |
| UTM-02 | `utm.medium` is null | 🟡 | No `utm_medium` on the final URL |
| UTM-03 | `utm.source` is null | 🟡 | No `utm_source` on the final URL |
| UTM-04 | `utm.campaign` is null | 🟡 | No `utm_campaign` on the final URL |
| UTM-05 | `utm.campaign` differs across links in the same email | 🟡 | Links use inconsistent `utm_campaign` values |
| UTM-06 | Every eligible link has source, medium=email, and campaign | 🟢 | `All links are UTMed and contain utm_medium=email` |

UTM-01 is deliberately 🟡, matching the shipped public tool. The email works and the recipient sees
nothing wrong; the damage is to reporting. Companies that treat attribution as critical should raise
it to 🔴 — a legitimate override.

## Images — from `images[]`

**Exclude from all checks:** any image where `likelyTrackingPixel` is true. Those are analytics
beacons, not design. `width`, `height`, and `src` are reported so you can second-guess that call.

| ID | Condition | Default | Message |
|---|---|---|---|
| IMG-01 | `src` is empty | 🔴 | Image has no source and will render as a broken icon |
| IMG-02 | `alt` is null (attribute absent) | 🟡 | Image is missing alt text |
| IMG-03 | `matchedPlaceholderPattern` is set | 🔴 | Placeholder artwork is still in place |
| IMG-04 | `check.ok` is false | 🔴 | Image will not load — returns HTTP {statusCode} |
| IMG-05 | `hiddenByInlineStyle` is true and not a pixel | 🟡 | Image is hidden by inline styles; may be a leftover |
| IMG-06 | Every non-pixel image loads | 🟢 | `All images render.` |

`alt=""` is **not** IMG-02. An empty alt is the correct, deliberate marking for decorative imagery.
Only a missing attribute (`alt` is `null`) counts.

## Tokens — from `tokens.*`

This section has no equivalent in the forwarded-email tool. A sent email has its tokens already
substituted, so none of this was previously knowable.

| ID | Condition | Default | Message |
|---|---|---|---|
| TOK-01 | `referenced[].defined` is false, `nearestDefinedNames` is empty | 🔴 | `{{my.{name}}}` is not defined in the owning program and will print literally |
| TOK-02 | `referenced[].defined` is false, `nearestDefinedNames` non-empty | 🔴 | `{{my.{name}}}` is not defined — did you mean `{suggestion}`? |
| TOK-03 | TOK-01/02 and `locations` includes `subject` | 🔴 | An undefined token in the **subject line** — this is the most visible possible place for it |
| TOK-04 | `referenced[].defined` false and `defaultValue` set | 🔴 | `{{my.{name}}}` is undefined, so recipients will read its fallback text: "{defaultValue}" |
| TOK-05 | `literalInSendingHtml.my` is non-empty | 🔴 | {n} token(s) will appear as raw `{{my.…}}` text in the inbox |
| TOK-06 | `defined[].valueIsEmpty` and `referencedByThisEmail` | 🟡 | `{{my.{name}}}` is defined but empty, so that copy renders as nothing |
| TOK-07 | `defined[].matchedPlaceholderPattern` set and referenced | 🟡 | `{{my.{name}}}` still holds placeholder copy: "{value}" |
| TOK-08 | `defined[].urlCheck.ok` is false and referenced | 🔴 | `{{my.{name}}}` holds a URL that does not resolve |
| TOK-09 | `defined[].urlCheck.utm.medium` is not `email` and referenced | 🟡 | `{{my.{name}}}` holds a URL with the wrong `utm_medium` |
| TOK-10 | `referenced[].inherited` is true | 🟢 informational | `{{my.{name}}}` is inherited from a parent program — editing it there changes this email too |
| TOK-11 | `referenced[].type` is `script block` or `iCalendar` | 🟡 | `{{my.{name}}}` is a `{type}` token; its contents were not inspected |
| TOK-12 | Every reference is defined and no literals survive | 🟢 | `All tokens resolve correctly.` |

**Never flag `literalInSendingHtml.lead`, `.system`, or `{{lead.*}}` / `{{system.*}}` anywhere.**
Marketo fills those in per recipient at send time. They are *supposed* to be unresolved in the asset.
Flagging them would fire on essentially every personalised email ever built, and it is the single
easiest way to make this report untrustworthy.

## Compliance — from `compliance.*`

| ID | Condition | Default | Message |
|---|---|---|---|
| CMP-01 | `unsubscribeLinks` is empty | 🔴 | No unsubscribe link found |
| CMP-02 | An unsubscribe link's `check.ok` is false | 🔴 | Unsubscribe link is broken |
| CMP-03 | `addressCandidates` is empty | 🟡 | No physical mailing address found in the visible copy |
| CMP-04 | `privacyPolicyLinks` is empty | 🟡 | No privacy policy link found |
| CMP-05 | A privacy link's `check.ok` is false | 🔴 | Privacy policy link is broken |
| CMP-06 | CMP-01 through CMP-05 all pass | 🟢 | `Nice work, you're CAN-SPAM compliant!` |

**Why CMP-03 is 🟡 and CMP-01 is 🔴**, since the two look symmetrical but are not:

Unsubscribe detection matches an href and anchor text. On real ESP footers that is near-perfectly
reliable, so a miss is a genuine finding worth stopping a send for.

Address detection matches visible text against postal-address shapes. It cannot know the sender's
jurisdiction, and it sees nothing at all when the address is baked into a footer image — which is
common. `addressCandidates[].matchedPattern` tells you which shape matched so you can judge for
yourself. A false 🔴 here tells a marketer "do not send" about a perfectly compliant email, and that
is exactly how a QA tool loses its credibility.

It stays 🟡 rather than 🟢 because CAN-SPAM does require the address. When you report CMP-03, say the
detection is a heuristic and ask the marketer to confirm — don't assert the address is missing.

## Social — from `links[].socialPlatform`

| ID | Condition | Default | Message |
|---|---|---|---|
| SOC-01 | A link with `socialPlatform` set has `check.ok` false | 🔴 | The {platform} link is broken |
| SOC-02 | A social link's URL is a bare domain with no account path | 🟡 | The {platform} link points at the homepage, not your profile |
| SOC-03 | A social link's `imageAlt` is null and `text` is empty | 🟡 | {platform} icon has no alt text |
| SOC-04 | Social links exist and all resolve | 🟢 | `Social links all resolve.` |
| SOC-05 | No link has `socialPlatform` set | 🟢 informational | `⚪ No social links found` |

SOC-05 is not a defect. Plenty of emails have no social icons by design.

## Copy quality — your judgement, not the tool's

`marketo_test_email` cannot assess these. Read `bodyText` and judge. Assign severities per this table.

| ID | Condition | Default |
|---|---|---|
| CPY-01 | Misspelling that reads as unintentional (exclude stylised brand names) | 🔴 |
| CPY-02 | Grammatical error that obscures the meaning | 🔴 |
| CPY-03 | Placeholder copy in the body: `Lorem ipsum`, `[INSERT CTA]`, `TBD`, `XXX` | 🔴 |
| CPY-04 | Unfinished sentence | 🔴 |
| CPY-05 | A link or button's label contradicts where it goes (compare `text` to `check.finalUrl`) | 🔴 |
| CPY-06 | The email contradicts itself, or parts don't serve its apparent purpose | 🔴 |
| CPY-07 | Alt text describes different content than this email's (e.g. last month's newsletter) | 🟡 |
| CPY-08 | Tone or readability concern; minor grammatical slip | 🟡 |
| CPY-09 | Copy is clean | 🟢 `Copy is free from any grammatical or spelling errors and does not contain placeholder text.` |

Rules that keep CPY-* from producing noise:

- **`{{lead.*}}` is not placeholder copy.** See the tokens section. This is the most common way to get
  CPY-03 wrong.
- **Ignore HTML comments.** Text inside `<!-- -->` is developer notes, not user-facing copy.
- **Ignore image filenames.** A typo in `hero-imge.png` doesn't matter if the image loads; IMG-04
  already covers whether it does.
- **Respect deliberate voice.** Lowercase brand names, sentence fragments used for rhythm, and playful
  punctuation are style choices, not errors.
- CPY-05 is the highest-value judgement here and the reason `links[]` carries both `text` and
  `finalUrl`. "Register for the webinar" pointing at a pricing page is exactly the kind of mistake
  that survives every automated check and embarrasses somebody.
