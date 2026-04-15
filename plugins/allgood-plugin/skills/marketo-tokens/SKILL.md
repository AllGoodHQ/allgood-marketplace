---
name: marketo-tokens
description: >
  Use this skill whenever a user wants to work with Marketo My Tokens —
  creating, updating, validating, or cleaning them up in a Marketo program.
  Triggers include: "create tokens in Marketo", "push tokens from this doc",
  "update the tokens in my program", "change this token value", "clean up old
  tokens", "set up My Tokens", "bulk edit tokens", "audit my program tokens",
  or any request involving `{{my.TokenName}}` in a Marketo program. Also
  triggers when the user shares a Google Doc with token references and asks
  to push them into a program, or when they name a program and ask to change
  values. Use this skill even if the user just says "edit the tokens" or
  "fix the tokens" — if it touches My Tokens in Marketo, this skill applies.
---

# Marketo Tokens

This skill handles end-to-end work with Marketo My Tokens in a program:

1. **Create** new tokens in a program from a Google Doc briefing (Workflow A)
2. **Update** values or metadata on tokens that already exist (Workflow B)
3. **Clean up** legacy / old-convention tokens after a conversion (Sub-flow C)

Every path runs through a preview + explicit confirm before any write, and
gates destructive writes against the program's live status. The goal is that
nothing unexpected lands in a program you care about.

---

## User Request

The user has requested: $ARGUMENTS

---

## Core Concepts

Four things matter for every workflow. Each has its own deeper reference —
load these when you need the detail.

| Concept | Why it matters | Reference |
|---|---|---|
| Token types (text, rich text, date, number, score, sfdc campaign, calendar) | Wrong type causes silent data corruption (RTE strips scripts, rich text breaks link tracking in text tokens, date format mismatches, etc.) | `references/token-editing-rules.md` |
| `folderType` (`"Program"` vs `"Folder"`) | Most common silent-failure cause. Wrong value = "token not found" or tokens created in wrong scope. | `references/mcp-tools.md` |
| Inheritance — LOCAL vs INHERITED | `get_program_tokens` returns only local tokens. Overriding an inherited token is **permanent** — rolling back is hard. | `references/token-editing-rules.md` → Token Inheritance |
| My Tokens (`{{my.X}}`) vs Template Variables (`${X}`) | Two separate systems in Marketo emails; this skill only handles My Tokens. | `references/token-editing-rules.md` → My Tokens vs Template Variables |

**My Tokens only.** This skill never creates or modifies `{{lead.*}}`, `{{system.*}}`, `{{company.*}}`, `{{program.*}}`, `{{campaign.*}}`, `{{member.*}}` — those are Marketo context tokens, not My Tokens.

---

## Universal Pre-flight (every workflow)

Run every step below before doing any workflow-specific work. Do not skip steps 3 or 5 — they're load-bearing for safety.

### 1. Identify the target program

```
marketo_get_programs_by_name(name="<program name>")
```

If multiple results come back, list them with workspace, folder path, and status so the user can disambiguate. Extract the numeric `id` from the chosen result.

### 2. Fetch program details

```
marketo_get_program_details(id=<id>)
```

Capture the program `status` (Draft / Approved / Active / Live) and note the channel, folder, and tags in passing.

### 3. ⚠️ Status gate — do not skip

If program status is **Approved, Active, or Live**, print this block before anything else:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  WARNING: This program is [STATUS]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Writing token values to a live program will affect:
  • Currently-scheduled sends that reference these tokens
  • Active nurture streams pulling from this program
  • Any asset (email, snippet, landing page) that renders {{my.*}} at send time

Before proceeding, confirm:
  1. You have reviewed which assets use these tokens
  2. You intend for changes to take effect immediately
  3. You have a rollback plan if something breaks

Reply with "yes, proceed on live program" (or equivalent explicit confirmation).
Anything else will abort.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Only proceed on explicit confirmation. Silent approval ("ok", "y", "sure") is not enough — require the user to acknowledge the live status.

For Draft programs, skip this block.

### 4. Fetch current tokens

```
marketo_get_program_tokens(programId=<id>)
```

**Important:** this returns only tokens defined locally on the program. Tokens inherited from parent folders are NOT returned. If the skill detects an `{{my.*}}` reference in source material that doesn't appear in the returned list, flag it as "possibly inherited — verify before treating as new."

### 5. Annotate for inheritance

For each token returned, mark source as `LOCAL`. For any token that's about to be written but doesn't appear in the returned list, it's unknown whether it's genuinely new or exists as an inherited token. Flag these for user review in the preview (see Preview Pattern).

---

## Workflow A — Create tokens from a Google Doc

### A.1 Collect inputs

Required before doing anything:

1. **Google Doc URL** — briefing doc with token table
2. **Marketo program name** — resolves to ID via pre-flight

If either is missing, ask. Don't proceed.

### A.2 Run universal pre-flight (steps 1–5 above)

### A.3 Read the doc

Extract file ID from `https://docs.google.com/document/d/{FILE_ID}/edit`, then:

```
read_file_content(fileId="{FILE_ID}")
```

Collect every `{{my.*}}` reference. **Skip** `{{lead.*}}`, `{{system.*}}`, `{{company.*}}`, `{{program.*}}`, `{{campaign.*}}`, `{{member.*}}`.

If the doc appears to have rich-text artifacts (smart quotes, split formatting on `{{ }}`), flag partial matches and ask the user to double-check rather than silently skipping them.

### A.4 Detect the doc's naming convention

Load `references/naming-conventions.md` now — it covers both the standard format and the old→new conversion.

- **New convention** — tokens already follow `NNN Label - Field Name` (e.g. `{{my.104 Invite 1 - Body Copy}}`). Extract as-is.
- **Old convention** — tokens use camelCase or `em{n}-` prefixes (e.g. `{{my.SubjectLine}}`, `{{my.em2-Copy}}`). Convert.

For old convention, follow the conversion steps in `naming-conventions.md`:
1. Group tokens into sections (by `em{n}-` prefix, or by nearest heading)
2. Assign numbers **sequentially by appearance within each block, starting at X00** (this is the canonical rule — the field-name lookup table is a *translation guide only*, not a number assignment)
3. Translate the field name using the lookup
4. Build `NNN Label - Field Name`

Show the user the full old→new mapping and ask for confirmation before continuing.

### A.5 Infer types

For each token, apply the heuristics from `references/token-editing-rules.md` → *Type Inference Heuristics*:

- `Body`, `Copy`, `Content` → `rich text`
- `Date`, `When` → `date`
- `Score` → `score`
- `Amount`, `Count`, `Number`, `Qty`, `Price` → `number`
- `Campaign` (SFDC context) → `sfdc campaign`
- `Calendar`, `iCal` → calendar (separate endpoint)
- `URL`, `Link`, `Image`, `Script`, `HTML`, `Pixel` → `text`
- anything else → `text`

The inferred type is shown in the preview and can be overridden per token.

### A.6 Pre-flight validation

For every token:

- [ ] Name ≤ 50 characters (if over, suggest an auto-shortened variant from `naming-conventions.md`)
- [ ] No spaces in name if the value will appear in a URL context (warn, don't auto-fix)
- [ ] Type string is an exact match (`rich text` not `richtext`, lowercase)

### A.7 Diff against existing tokens

For each token, compute status:

| Status | Meaning |
|---|---|
| NEW | Doesn't exist locally on the program. Safe to create. |
| UPDATE (local) | Exists locally. Will overwrite unless user opts to preserve. |
| UPDATE (overrides inherited) | Not in local list but referenced upstream — writing here **permanently breaks inheritance**. Surface this loudly. |
| CONFLICT (type mismatch) | Exists locally but existing type ≠ new type. Cannot be updated — requires delete + recreate. |
| SKIP | User explicitly excluded, or inherited and we agreed to leave inheritance intact. |

### A.8 Preview and confirm

Use the [Preview Pattern](#preview-pattern) below. Default is **preserve existing values** — every UPDATE row requires explicit user approval (per-token or a blanket "overwrite all UPDATEs"). NEW rows execute without individual approval once the overall preview is confirmed.

### A.9 Execute

Prefer the bulk wrapper:

```
marketo_create_or_update_tokens(
  programId=<id>,
  tokens=[
    {"name": "100 Invite 1 - Subject Line", "type": "text", "value": "Edit me."},
    {"name": "104 Invite 1 - Body Copy", "type": "rich text", "value": "<p>Edit me.</p>"},
    ...
  ]
)
```

Notes:
- There is no real bulk endpoint in Marketo. This wrapper loops under the hood — respect the 100-calls-per-20s rate limit.
- If the wrapper is unavailable, fall back to looping `create_token(folderType="Program")` with pacing (see `references/mcp-tools.md`).
- Always pass `folderType="Program"` for program-scoped writes.
- Never swallow per-token errors — capture the failure for the report.

**Placeholders** for NEW tokens (unless user supplied real values):

| Type | Placeholder |
|---|---|
| `text` | `Edit me.` |
| `rich text` | `<p>Edit me.</p>` |
| `date` | `2026-01-01` |
| `number` | `0` |
| `score` | `0` |
| `sfdc campaign` | empty (user must supply Campaign ID) |

### A.10 Report

Use the [Reporting Pattern](#reporting-pattern).

### A.11 Offer cleanup sub-flow

If this was an old→new conversion, the old-convention tokens still exist locally. After reporting success, offer to run [Sub-flow C (cleanup)](#sub-flow-c--clean-up-legacy-tokens). Do not run it automatically.

---

## Workflow B — Update existing tokens in a program

### B.1 Collect inputs

- **Program name** (required)
- **What to change** — either the user specifies up front, or we show current state and let them point to changes

### B.2 Run universal pre-flight

### B.3 Present current state

Show the tokens currently on the program, with source (LOCAL / INHERITED), type, and a truncated value preview. This is the starting point for the user to describe changes.

If the user wants to change inherited tokens, warn: overriding an inherited token at a child level is **permanent** — the parent value won't flow down again even after the local override is deleted. See `references/token-editing-rules.md` → *Critical limitation: overridden tokens cannot be re-inherited*.

### B.4 Validate proposed changes

For each change, apply per-type rules from `references/token-editing-rules.md`:

- **Text** — preserve entities/whitespace exactly; warn on links (won't be tracked); warn on `\n` without `<br>` (batch vs trigger inconsistency).
- **Rich Text** — strip zero-width Unicode (U+200B, U+FEFF, U+200C, U+200D); strip `<mark>`; convert `<code>` to monospace `<span>`; require absolute URLs + inline color on `<a>`; flag any `<script>`, `<style>`, `<video>`, `{{my.X}}` nesting, or CSS classes (all will be stripped or broken).
- **Date** — enforce `yyyy-MM-dd` output; interpret ambiguous input as `MM-dd-yyyy` (US).
- **Number** — enforce 0 to 99,999,999 (UI-compatible range) unless user confirms API-only usage.
- **Score** — enforce signed 32-bit integer range; no floats.

### B.5 Detect CONFLICTs and OVERRIDES

- **Type CONFLICT**: existing type ≠ new type → cannot update; requires delete + recreate. Flag in preview.
- **Inheritance OVERRIDE**: user is writing a value for a token currently only inherited (not local) → permanent override. Flag in preview with the warning from B.3.

### B.6 Preview and confirm

Use the [Preview Pattern](#preview-pattern). Every UPDATE requires explicit user approval.

### B.7 Execute and report

Same as A.9 and A.10. For CONFLICT tokens the user chose to resolve: this requires a two-step delete-then-recreate, which is destructive — route those through [Sub-flow C](#sub-flow-c--clean-up-legacy-tokens) first, then re-enter execute for the recreate.

---

## Sub-flow C — Clean up legacy tokens

Triggered from the end of Workflow A (after a conversion) or on explicit user request ("delete the old tokens", "clean up `em2-` tokens"). Never runs automatically.

### C.1 Loud warning block

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  LEGACY TOKEN DELETION — READ BEFORE PROCEEDING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tokens being deleted may still be referenced in:
  • Email HTML and templates
  • Snippets
  • Landing pages
  • Smart campaign flow steps

This sub-flow does NOT scan for references. If a deleted token is
referenced by a live asset, it will render as literal `{{my.OldName}}`
text in emails sent to leads — a visible bug.

Before proceeding:
  1. Confirm no assets reference these tokens (manually or via audit)
  2. Understand that deletion is immediate and cannot be undone

Reply "I have confirmed no references" to proceed, or "cancel" to abort.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Point the user at use case #2 in `use-cases.md` (token usage audit) as the eventual replacement for manual confirmation.

### C.2 Per-token preview

List each deletion candidate:

```
  #   Name                        Type        Current Value (truncated)
  ─────────────────────────────────────────────────────────────────────
  1   SubjectLine                 text        "Join us for the webinar…"
  2   em2-Copy                    rich text   "<p>Register now…"
  3   CTA1URL                     text        "example.com/register"
  ...
```

### C.3 Per-token confirm

Ask for confirmation **per token** — not bulk. If the user wants to skip confirmation for the rest ("delete all the remaining"), let them, but surface the remaining list first.

### C.4 Execute

```
delete_token(id=<program_id>, name="<token name>", type="<type>", folderType="Program")
```

Note: no allGood wrapper exists for `delete_token` — use Direct MCP. `folderType="Program"` is required.

### C.5 Report

Use [Reporting Pattern](#reporting-pattern).

---

## Preview Pattern

Shown before any write. Always this column layout:

```
Ready to create/update 15 tokens in program: [Program Name] (ID: 12345)
Program status: Draft

  #    Token Name                      Type        Source      Status                       Notes
  ───────────────────────────────────────────────────────────────────────────────────────────────────────────────
  100  Invite 1 - Subject Line         text        —           NEW                          —
  101  Invite 1 - Banner Image         text        —           NEW                          —
  102  Invite 1 - Preheader            text        —           NEW                          —
  104  Invite 1 - Body Copy            rich text   —           NEW                          —
  105  Invite 1 - CTA                  text        LOCAL       UPDATE (current: "Register") Needs explicit approval
  106  Invite 1 - UTM                  text        —           NEW                          Name "Invite 1 - UTM" has spaces — warn if used in URL
  001  Webinar Reg URL                 text        INHERITED   UPDATE (overrides inherited) ⚠️ Permanent override — inheritance will not re-establish
  ...
  999  Very Long Descriptive Name Long  text       —           BLOCKED                      51 chars > 50 limit; suggest: "Very Long Descriptive Name"
  200  Invite 2 - Subject Line         rich text   LOCAL       CONFLICT                     Existing type is text; requires delete + recreate
```

Rules:
- `Source`: `LOCAL` (defined locally), `INHERITED` (resolved from parent), `—` (not in current local list)
- `Status`: `NEW`, `UPDATE`, `UPDATE (overrides inherited)`, `CONFLICT`, `SKIP`, `BLOCKED`
- `Notes`: any warning that applies (tracked-link risk, inheritance break, 50-char, URL-context space, type conflict remediation)

After the table, always print:

```
Defaults:
  NEW tokens       → will be created with placeholder values
  UPDATE           → will preserve existing values UNLESS you approve per token
  CONFLICT/BLOCKED → will NOT execute; resolve first
  INHERITED        → warning requires explicit acknowledgment

Reply with one of:
  • "proceed" — creates all NEW, skips all UPDATEs/CONFLICT/BLOCKED
  • "proceed with updates" — creates all NEW and overwrites all UPDATE rows
  • "edit <#>" — change a row (type override, name change, skip)
  • "cancel"
```

---

## Execution Pattern

Regardless of workflow:

- First choice: allGood wrapper (`marketo_create_or_update_tokens` / `marketo_create_or_update_token`). Fallback: Direct MCP `create_token` loop.
- Always pass `folderType="Program"` for program-scoped writes.
- Respect rate limits: 100 calls / 20 seconds, max 10 concurrent. For runs >100 tokens, pace explicitly (the wrapper may not).
- Capture per-token outcomes. Never silently swallow errors.
- For `delete_token`: use Direct MCP only (no wrapper exists).
- For calendar tokens: use `create_calendar_token` (Direct MCP) — separate endpoint.

---

## Reporting Pattern

After execution:

```
Token Operation Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Program:  [Program Name] (ID: 12345)
Status:   Draft

✅  Created:   12 tokens
🔁  Updated:   2 tokens
⏭️   Skipped:   1 token  (existed, user chose preserve)
❌  Failed:    0 tokens
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Not executed:
  ⚠️  1 CONFLICT  (200 Invite 2 - Subject Line — existing type mismatch)
  ⚠️  1 BLOCKED   (name exceeds 50-char limit)
```

If any tokens failed, list each with its error message beneath the summary.

If Workflow A converted tokens from an old convention, end the report with:

```
Legacy tokens still present in program:
  • SubjectLine, Preheader, em2-Copy, …
Run the cleanup sub-flow when you're ready. Before deleting, confirm
no assets still reference the old names.
```

---

## Reference Files

| File | Load when |
|---|---|
| `references/token-editing-rules.md` | Type decisions, per-type validation, API mechanics, inheritance semantics, Rich Text gotchas, My Tokens vs Template Variables |
| `references/naming-conventions.md` | Detecting the doc's convention, converting old→new names, 50-char check, tokens-to-skip |
| `references/mcp-tools.md` | Tool selection (allGood wrapper vs Direct MCP), `folderType` gotcha, rate limits, fallback pattern |
| `use-cases.md` | When a user asks for something the skill doesn't yet cover (audit, inventory, cloning, change tracking) |
