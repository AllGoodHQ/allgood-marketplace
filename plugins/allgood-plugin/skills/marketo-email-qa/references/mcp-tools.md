# MCP Tools for Email QA

> Loaded by `marketo-email-qa/SKILL.md` when it needs the tool contract or a fallback path.

## Tool selection

| Need | First choice | Fallback |
|---|---|---|
| Find the email by name | `marketo_get_programs_by_name` → read its emails | Ask for the email ID |
| QA measurements | `marketo_test_email` | `marketo_get_email_details` (see below) |
| Token definitions for context | Already inside `marketo_test_email` | `marketo_get_program_tokens` |
| Fix a token you found | `marketo_create_or_update_token` | — |

## `marketo_test_email`

```
marketo_test_email(emailId=<id>)
marketo_test_email(emailId=<id>, checkLinks=false)
```

| Arg | Required | Meaning |
|---|---|---|
| `emailId` | yes | The Marketo email ID |
| `checkLinks` | no, default `true` | Set `false` to skip all network requests. Links and images come back with `check: null`. |

**It returns measurements, not verdicts.** No severities, no flags, no risk level. Apply
`references/qa-policy.md` to it. If you find yourself reading a severity out of the response, you are
reading the wrong field — there aren't any.

### Response shape

```
{
  "email": {
    "id", "name", "subject", "fromName", "fromEmail", "replyEmail",
    "preHeader", "templateId", "programId", "previewUrl",
    "subjectLength", "preHeaderLength", "preHeaderEqualsSubject",
    "fromEmailIsValidFormat", "replyEmailIsValidFormat"
  },
  "bodyText": "visible copy, whitespace-collapsed",
  "links": [ { href, text, ariaLabel, title, imageAlt, scheme,
               hiddenByInlineStyle, occurrences, socialPlatform,
               isUnsubscribe, isPrivacyPolicy, check } ],
  "images": [ { src, alt, width, height, inlineStyle, hiddenByInlineStyle,
                likelyTrackingPixel, matchedPlaceholderPattern, check } ],
  "tokens": {
    "referenced": [ { name, rawKey, defaultValue, locations, defined, type,
                      value, inherited, overridden, nearestDefinedNames } ],
    "defined":    [ { name, type, value, inherited, overridden,
                      referencedByThisEmail, valueIsEmpty,
                      matchedPlaceholderPattern, urlCheck } ],
    "literalInSendingHtml": { my: [], lead: [], system: [], other: [] }
  },
  "compliance": {
    "unsubscribeLinks": [ ...links... ],
    "privacyPolicyLinks": [ ...links... ],
    "addressCandidates": [ { text, matchedPattern } ]
  },
  "linksChecked": true,
  "checksSkipped": [ { check, reason } ]
}
```

A `check` object, on a link, an image, or a token's URL:

```
{
  "url":           "the URL as authored",
  "finalUrl":      "where it landed after redirects",
  "statusCode":    200,
  "ok":            true,          // statusCode is 200-399
  "redirectCount": 2,
  "error":         null,          // set on DNS/TLS/timeout failure
  "skipped":       null,          // "unsupported-scheme" | "private-host" | "malformed"
  "utm":           { source, medium, campaign, term, content }
}
```

### Fields that are easy to misread

**`utm` is read off `finalUrl`, never off `url`.** This is the whole reason the tool follows redirects
by hand. A Marketo click-tracking link carries no campaign parameters of its own; only the page it
lands on does. So never report a tracking domain as "missing UTMs" — check `utm` and be done.

**`literalInSendingHtml` is split by namespace because the halves mean opposite things.**

| Group | Meaning |
|---|---|
| `my` | **A defect.** Prints as raw `{{my.Foo}}` text in the recipient's inbox. |
| `lead` | **Normal.** Marketo fills these in per recipient at send time. |
| `system` | **Normal.** Same. |
| `other` | Worth a look — an unrecognised namespace. |

Flagging `lead` or `system` tokens would fire on nearly every personalised email ever built. Don't.

**`nearestDefinedNames`** is a typo suggestion, populated only when `defined` is `false`. If a
reference to `my.Headine` comes back with `["Headline"]`, say so — "did you mean `my.Headline`?" is far
more useful than "token undefined".

**`defaultValue`** is what recipients actually read when a token is undefined.
`{{my.Title:default=edit me}}` on a missing token puts the literal words "edit me" in the inbox. Quote
it in the finding.

**`likelyTrackingPixel`** excludes analytics beacons from image checks. `width`, `height`, `src`, and
`inlineStyle` are all reported alongside it, so if the classification looks wrong for a given email you
can override it.

**`alt: null` differs from `alt: ""`.** Null means the attribute is absent (a finding). Empty string
means the author deliberately marked the image decorative (correct, not a finding).

**`checksSkipped` is not decoration.** Report it. A check that could not run must not read like a check
that passed.

### Errors

The tool never throws — failures come back as a plain-text message instead of JSON. Two you'll meet:

| Message contains | What to do |
|---|---|
| `not found` | The email ID is wrong. Ask for the right one, or search by program name. |
| `Marketo integration` / `authorization` | The tenant has no Marketo connection. Say so; don't retry. |

## Fallback: no `marketo_test_email` available

If the tool isn't registered on the endpoint you're connected to, you can still do a reduced pass with
`marketo_get_email_details(emailId=<id>)`, which returns email metadata plus `fullHtml`.

What you lose, and must say you lost:

- **Link and image resolution.** You cannot fetch URLs, so you cannot know what's broken. Do not guess
  from the URL's appearance.
- **UTMs on final URLs.** You'll see the authored href only. A click-tracker's href tells you nothing
  about the landing page's parameters, so don't report UTM findings at all.
- **Token definition checks.** `marketo_get_email_details` resolves tokens server-side, so you cannot
  tell an undefined token from a defined one. You can pair it with
  `marketo_get_program_tokens(programId=<id>)` and compare by hand, remembering that Marketo returns
  names **with** the `my.` prefix.

What still works: metadata checks, copy quality, alt-text presence, and unsubscribe/privacy link
presence — all from parsing `fullHtml`.

Lead with the limitation. A report that quietly omits link checking reads like a report where the links
were fine.
