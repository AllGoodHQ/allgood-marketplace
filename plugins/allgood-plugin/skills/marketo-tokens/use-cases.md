# Marketo Tokens — High-Impact Use Cases

Tracker for the capabilities the `marketo-tokens` skill should support, now or
later. Each entry records what the capability is, why it's in demand, how it
maps to the available APIs, and whether this skill covers it today.

**Coverage legend**

- **covered** — the current SKILL.md handles this end-to-end
- **partial** — the skill handles part of it; gaps noted
- **future** — not in this skill yet; capture requirements for a follow-up

## Coverage summary

```
┌─────┬────────────────────────────────────────┬──────────────────────────────────────┐
│  #  │                Use case                │               Coverage               │
├─────┼────────────────────────────────────────┼──────────────────────────────────────┤
│ 1   │ Bulk token read and update             │ covered                              │
├─────┼────────────────────────────────────────┼──────────────────────────────────────┤
│ 2   │ Token usage audit                      │ future                               │
├─────┼────────────────────────────────────────┼──────────────────────────────────────┤
│ 3   │ Token deletion and cleanup             │ partial                              │
├─────┼────────────────────────────────────────┼──────────────────────────────────────┤
│ 4   │ Token inventory and search             │ future                               │
├─────┼────────────────────────────────────────┼──────────────────────────────────────┤
│ 5   │ Inheritance visualization              │ partial                              │
├─────┼────────────────────────────────────────┼──────────────────────────────────────┤
│ 6   │ Cross-program token cloning            │ future                               │
├─────┼────────────────────────────────────────┼──────────────────────────────────────┤
│ 7   │ Token change tracking                  │ future                               │
├─────┼────────────────────────────────────────┼──────────────────────────────────────┤
│ 8   │ Token validation and formatting        │ covered                              │
└─────┴────────────────────────────────────────┴──────────────────────────────────────┘
```

---

## 1. Bulk token read and update

- **Demand signal:** The single most requested capability. Teams maintaining many programs (nurtures, event series, recurring sends) need to inspect and update dozens of tokens per program without clicking through the UI.
- **API feasibility:** Directly addressable. Loop logic over `create_token` (upsert) + `get_tokens_by_folder` for reads. allGood's `marketo_create_or_update_tokens` wrapper provides a convenience surface.
- **Coverage:** **covered** — Workflow A (create from Google Doc) and Workflow B (update existing) both operate in bulk with preview/confirm.
- **Design notes:** No real bulk API endpoint exists — every token is a separate POST. Rate limits (100/20s, max 10 concurrent) apply. Pacing should be built in for >100-token runs.

---

## 2. Token usage audit

- **Demand signal:** Before changing or deleting a token, teams need to know where it's referenced — across emails, templates, snippets, landing pages. The UI provides no global search.
- **API feasibility:** Requires fetching asset HTML via API (emails, templates, snippets, landing pages) and regex-scanning for `{{my.TokenName}}`. Each asset type has its own content endpoint.
- **Coverage:** **future**.
- **Open questions:**
  - Which asset types should the audit cover first? (Proposal: emails + snippets + templates; landing pages later.)
  - Fuzzy match on token names (e.g. find `Subject` whether token is `100 Invite 1 - Subject Line` or `SubjectLine`)?
  - Output format: report + CSV? Inline preview?
- **Design notes:** This is the unlock that makes cleanup safe. Until it exists, Workflow C relies on the user manually confirming references.

---

## 3. Token deletion and cleanup

- **Demand signal:** There's a well-known decade-old UI bug that fails to delete certain tokens. The API delete endpoint works where the UI fails.
- **API feasibility:** `delete_token` (Direct MCP) works reliably with `folderType="Program"`.
- **Coverage:** **partial** — Workflow C sub-flow in SKILL.md covers per-program cleanup with heavy warnings and per-token confirm. Does not perform a cross-program sweep, and does not auto-check for references (see use case #2).
- **Open questions:**
  - Bulk-sweep mode across many programs? Needs strict safety rails.
  - Pair with audit (use case #2) so deletion only offers tokens with zero references found.

---

## 4. Token inventory and search

- **Demand signal:** A global registry — "show me every My Token across the instance, and let me search/filter." Useful for governance, de-duplication, naming-convention audits.
- **API feasibility:** Requires folder-tree walk via `browse_folders` + `get_tokens_by_folder` on each node. Potentially expensive — hundreds of folder calls.
- **Coverage:** **future**.
- **Open questions:**
  - Scope: one workspace at a time, or the whole instance?
  - Caching — rebuild nightly vs on-demand?
  - Cross-instance search (multi-tenant) — is that in scope?

---

## 5. Inheritance visualization

- **Demand signal:** Token resolution in Marketo is based on folder hierarchy, and overrides are permanent once set. Teams need to see where a token is defined, what inherits from it, and where it's been overridden.
- **API feasibility:** Built from `browse_folders` + `get_tokens_by_folder` calls walking both up and down from a given program.
- **Coverage:** **partial** — the skill's preview flags each existing token as LOCAL or INHERITED and warns on permanent override breaks. It does not render a tree.
- **Open questions:**
  - Rendering format: text tree, table, or interactive diagram?
  - Highlight conflict classes: same token, different value, different level.

---

## 6. Cross-program token cloning

- **Demand signal:** When spinning up a new program from a template (invitations, TYFA, SWMY), teams want to copy the parent program's token set wholesale to the new one.
- **API feasibility:** `get_tokens_by_folder` on source + loop `create_token` on target. No single-call clone exists.
- **Coverage:** **future**.
- **Open questions:**
  - Should values come along, or just names and types (placeholder-filled)?
  - How to handle naming-block collisions (e.g. source has `100 Invite 1 -`, target already has a `100 …`)?

---

## 7. Token change tracking

- **Demand signal:** Teams want to know when a token value changed, by whom, and what the previous value was. Useful for audit trails and incident response.
- **API feasibility:** No webhook exists. Requires periodic polling of `get_tokens_by_folder` with snapshotting to detect diffs.
- **Coverage:** **future**.
- **Open questions:**
  - Storage — where do snapshots live? Frequency?
  - What's the delivery surface (Slack, email digest, in-UI log)?
  - "By whom" is not available from the API — is value + timestamp enough?

---

## 8. Token validation and formatting

- **Demand signal:** Writing values that Marketo silently mangles (Rich Text zero-width spaces, date format mismatches, `<script>` in rich text) is a leading cause of "tokens don't work" incidents.
- **API feasibility:** Pure client-side validation before POST. No new endpoints needed.
- **Coverage:** **covered** — the validation checklist in `references/token-editing-rules.md` covers all 5 primary types. Workflows A and B apply it during preview.
- **Design notes:** Good candidate for a standalone script in a future version so validation can run without the full workflow (e.g. as a pre-commit check on a briefing doc's token values).

---

## Triage summary

| # | Use case | Coverage |
|---|---|---|
| 1 | Bulk read/update | covered |
| 2 | Usage audit | future |
| 3 | Deletion/cleanup | partial |
| 4 | Inventory/search | future |
| 5 | Inheritance visualization | partial |
| 6 | Cross-program cloning | future |
| 7 | Change tracking | future |
| 8 | Validation/formatting | covered |

Next most valuable additions: **#2 (audit)** — unlocks safe cleanup — and **#6 (cloning)** — the highest-frequency new-program workflow.
