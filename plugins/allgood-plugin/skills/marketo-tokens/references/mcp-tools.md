# Marketo MCP Tools — Reference for Token Workflows

> Loaded by `marketo-tokens/SKILL.md` when the model needs to pick the right
> MCP tool for a token operation. Curated subset of the full Marketo MCP
> catalog — only the tokens, folders, and programs tools that matter for
> the workflows in SKILL.md.

---

## Two MCP paths — when to use which

Two MCP servers expose Marketo:

| Path | Prefix | Characteristics | Use when |
|---|---|---|---|
| **allGood wrapper** | `marketo_*` (e.g. `marketo_create_or_update_tokens`) | Convenience wrappers — batch-friendly, opinionated defaults, loops under the hood. Maps to allGood's workflow. | Preferred for multi-token work (create-many, update-many). First choice. |
| **Direct Marketo MCP** | no prefix (e.g. `create_token`, `delete_token`) | One-to-one with Marketo's REST API. Covers operations the wrappers don't expose. | Fallback when a wrapper is missing. Required for `delete_token`, `create_calendar_token`, single-token ops when throttling matters. |

**Fallback pattern:** if an allGood wrapper is unavailable, loop the equivalent direct MCP tool while respecting the rate limit (100 calls / 20 seconds). Do not retry past transient 429s without backoff.

---

## `folderType` — the most common silent-failure cause

Every token tool accepts a `folderType` parameter: either `"Folder"` or `"Program"`. It defaults to `"Folder"` when omitted, and Marketo does NOT search both. Wrong `folderType` produces "token not found" errors (on read) or tokens created in the wrong scope (on write).

**Rule of thumb for this skill:**
- Target is a program → `folderType="Program"`
- Target is a workspace/marketing folder → `folderType="Folder"`

Set it explicitly on every call. Never rely on the default.

---

## Tokens (5 tools)

| Tool | Path | Use | Required | Optional |
|---|---|---|---|---|
| `create_token` | Direct | Create or upsert a My Token in a folder or program. Supports `date`, `number`, `rich text`, `score`, `sfdc campaign`, `text`. | `id` (int), `name` (str), `type` (str), `value` (str) | `folderType` (str, default `"Folder"`) |
| `create_calendar_token` | Direct | Create a calendar (iCalendar) token. Separate endpoint from `create_token`. | `id` (int), `name` (str), `value` (str) | `folderType` (str, default `"Folder"`) |
| `get_calendar_tokens` | Direct | List calendar tokens on a folder/program. | `id` (int) | `folderType` (str, default `"Folder"`) |
| `get_tokens_by_folder` | Direct | List all (non-calendar) My Tokens directly defined on a folder/program. Does NOT return inherited tokens. | `id` (int), `folderType` (str) | — |
| `delete_token` | Direct | Delete a My Token by name and type. **Destructive — no dry-run, no undo.** Does not check whether the token is referenced by any asset. | `id` (int), `name` (str), `type` (str) | `folderType` (str, default `"Folder"`) |

### allGood wrappers for tokens

| Wrapper | Use | Notes |
|---|---|---|
| `marketo_create_or_update_token` | Upsert a single token in a program. | Thin wrapper around `create_token`. |
| `marketo_create_or_update_tokens` | Upsert many tokens in one call. | **No real bulk endpoint exists** (see `token-editing-rules.md` → API Mechanics). This wrapper loops `create_token` under the hood — respect rate limits. |
| `marketo_get_program_tokens` | List tokens on a program. | Maps to `get_tokens_by_folder` with `folderType="Program"`. LOCAL tokens only — inherited tokens are not returned. |

### What's NOT in allGood wrappers (use Direct MCP)

- **Delete** — no `marketo_delete_token` wrapper; use `delete_token` directly.
- **Calendar tokens** — no allGood wrapper; use `create_calendar_token` / `get_calendar_tokens`.

---

## Programs (selected — 4 tools)

| Tool | Path | Use | Required |
|---|---|---|---|
| `get_program_by_name` | Direct | Find a program by exact name. Returns ID, status, channel, folder, tags. | `name` (str) |
| `marketo_get_programs_by_name` | allGood | Fuzzy name search for programs — returns multiple matches for disambiguation. | `name` (str) |
| `marketo_get_program_details` | allGood | **Critical for pre-flight.** Returns program status (Draft/Approved/Active), folder, channel, tags. Use this to gate writes against live programs. | `id` (int) |
| `browse_programs` | Direct | Paginated list of programs, filterable by status and date range. | — |

**Pre-flight order** (every workflow):
1. `marketo_get_programs_by_name` → disambiguate if multiple
2. `marketo_get_program_details(id=<chosen>)` → **status gate**
3. If status is Approved/Active/Live → print loud warning, require explicit user confirmation before any write

---

## Folders (selected — 3 tools)

| Tool | Path | Use |
|---|---|---|
| `get_folder_by_id` | Direct | Fetch folder details when walking the tree to resolve inherited tokens. |
| `get_folder_by_name` | Direct | Find a folder by name (for folder-scoped token operations). |
| `browse_folders` | Direct | Walk the folder hierarchy. Needed for inheritance visualization or full token inventory — out of scope for current workflows; see `use-cases.md`. |

---

## Rate Limits & Body Rules

| Limit | Value |
|---|---|
| Calls per 20 seconds | 100 |
| Calls per day | 50,000 |
| Max concurrent | 10 |
| Body size | 1 MB per request |
| URI length | 8 KB max |
| Bulk token endpoint | **Does not exist** — every token is a separate POST |

For Rich Text token values, always pass content in the POST body, never as a URL query parameter. URI length will truncate large Rich Text silently.

When creating >100 tokens in one run, the allGood wrapper should pace; if pacing is not built in, chunk calls yourself and insert 20-second waits after each 100.

---

## Tool-Selection Cheat Sheet

| Workflow step | First choice | Fallback |
|---|---|---|
| Find program by name | `marketo_get_programs_by_name` | `get_program_by_name` |
| Check program status | `marketo_get_program_details` | `browse_programs` + filter |
| List current tokens on program | `marketo_get_program_tokens` | `get_tokens_by_folder(folderType="Program")` |
| Create/update one token | `marketo_create_or_update_token` | `create_token(folderType="Program")` |
| Create/update many tokens | `marketo_create_or_update_tokens` | loop `create_token` with rate limiting |
| Delete a token | `delete_token(folderType="Program")` | — (no wrapper) |
| Create a calendar token | `create_calendar_token(folderType="Program")` | — (no wrapper) |
