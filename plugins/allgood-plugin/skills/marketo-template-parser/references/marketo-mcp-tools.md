# Marketo MCP Tools (Template-Relevant)

Reference for working with Marketo assets via MCP when a user points at a live email rather than a local `.html` file.

## Important scope note

The MCP tools exposed are **email-level and snippet-level, not template-level.** You can:

- Read the HTML of a specific email built from a template
- Write edits to a specific email's editable content sections
- Read/write snippets that templates reference

You **cannot** edit the template asset itself via MCP — that still happens in the Marketo UI. If the user's ask implies changing the underlying template (e.g., "add a new module to this template for all future emails"), surface this limitation and suggest they make the change in Marketo, then use this skill on the updated template file.

---

## Reading an email (to parse with this skill's scripts)

Use when a user says "pull email 12345 and check it" or "review this email in Marketo."

| Tool | Purpose |
|---|---|
| `get_email_by_name(name, folder?, status?)` | Look up an email by name. Returns ID, folder, status, timestamps. Use this first if the user gave a name rather than an ID. |
| `get_email_by_id(id, status?)` | Fetch full metadata for a known email ID. |
| `get_email_content(id, status?)` | Returns all editable content sections with their HTML/text values, `htmlId`s, types, and section names. **This is the main tool for pulling content to analyze.** |
| `browse_emails2(folder?, status?, ...)` | Paginated list when the user wants to search/filter without a specific name. |

**Workflow snippet — pulling for analysis:**
1. `get_email_by_name` or `get_email_by_id` to confirm the email exists and capture its ID
2. `get_email_content(id)` to get all editable sections
3. Reassemble the HTML (or work section-by-section) and run it through `scripts/validate.py`, `scripts/lint_email.py`, `scripts/list_modules.py`, etc.

---

## Writing edits back

Use after the user has approved a fix or modification.

| Tool | Purpose |
|---|---|
| `update_email_content(id, htmlId, value, type?)` | Patch one editable section. The `htmlId` comes from `get_email_content`. `type` defaults to `"Text"` — use `"DynamicContent"`, `"Snippet"`, etc. when appropriate. |
| `approve_email(id)` | **Required** after edits. Until approved, the changes sit in a draft and won't be used by campaigns. |

**Safety pattern:** always confirm with the user before calling `update_email_content` or `approve_email`. Show a diff/preview of what's changing. Never auto-approve.

Related (rare, but useful to know):
- The email APIs do not expose a universal "discard draft" for emails in `marketo.mcp.md`, but `discard_form_draft` / `discard_snippet_draft` follow the same pattern if the user needs to bail on changes.

---

## Tokens (My Tokens)

Templates often reference `{{my.TokenName}}`. When fixing a template issue tied to token values, or auditing what a program exposes, these are the tools.

| Tool | Purpose |
|---|---|
| `get_tokens_by_folder(id, folderType)` | List all My Tokens in a folder or program. `folderType` is usually `"Folder"` or `"Program"`. |
| `create_token(id, name, type, value, folderType?)` | Create a My Token. Types: `date`, `number`, `rich text`, `score`, `sfdc campaign`, `text`. |
| `delete_token(id, name, type, folderType?)` | Remove a token. |

**allGood MCP equivalents** (if operating in the allGood environment):
- `marketo_get_program_tokens(programId)` — bulk read
- `marketo_create_or_update_token(...)` / `marketo_create_or_update_tokens(...)` — upsert one or many
- `marketo_get_programs_by_name(name)` — resolve program name → ID

Prefer the bulk upsert (`marketo_create_or_update_tokens`) when touching more than one token.

---

## Snippets

Templates reference snippets via `mktoSnippet` elements. Editing or updating a snippet propagates to every template that uses it.

| Tool | Purpose |
|---|---|
| `get_snippet_by_id(id, status?)` | Metadata. |
| `get_snippet_content(id, status?)` | Actual HTML or text body. |
| `update_snippet_content(id, type, content)` | Patch the body. `type` must match the snippet's content type. |
| `approve_snippet(id)` | Required after edits. |
| `get_snippet_dynamic_content(id)` | Segment-specific variations (dynamic content). |
| `update_snippet_dynamic_content(snippetId, segmentId, value, type)` | Patch one segment variation. |

**Use with care:** changing a snippet affects everywhere it's used. Run any impact check available before editing.

---

## Impact analysis (before destructive edits)

Before editing a shared asset, check what depends on it.

| Tool | Purpose |
|---|---|
| `get_forms_used_by(id)` | Assets that use a given form. (No direct email equivalent is exposed — call out to the user if they're editing an email widely referenced and you want a dependency check.) |
| `get_smart_campaign_used_by(id)` | Assets referencing a smart campaign. |
| `get_smart_list_used_by(id)` | Assets referencing a smart list. |

---

## Related MCPs

- **allGood MCP** (`marketo_*` tools) — allGood's internal wrapper. Fewer tools but tuned for common workflows: `marketo_get_email_details`, `marketo_get_program_details`, `marketo_get_program_tokens`, `marketo_get_programs_by_name`, `marketo_create_or_update_token(s)`, `marketo_update_program_tags`.
- **Marketo MCP** (the larger tool surface listed above) — full REST coverage for forms, emails, snippets, programs, tokens, folders, smart campaigns, smart lists, leads, lists, bulk ops.

When both are available, prefer whichever gives the simplest path to the user's goal. For token work, the allGood bulk upsert (`marketo_create_or_update_tokens`) is typically easier than orchestrating individual `create_token` calls.
