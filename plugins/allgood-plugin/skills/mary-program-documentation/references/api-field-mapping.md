# MCP Tool Chain & Field Mapping

This reference documents which MCP tools to call, in what order, and how to map their
response fields to document sections.

---

## Two Tool Paths

Two sets of MCP tools are available:

| Path | Prefix | Best for |
|---|---|---|
| **allGood wrappers** | `marketo_*` | Program search, token read/write, email details |
| **Direct Marketo MCP** | No prefix (e.g. `get_program_by_id`) | Smart campaigns, flow steps, smart lists, forms, folders |

Use both. The allGood wrappers are convenient for initial search and tokens. The direct
tools are required for smart campaign detail (flow steps, smart list rules) and forms.

---

## Call Sequence

Follow this order. Each step depends on the previous one.

### 1. Resolve Program ID

```
marketo_get_programs_by_name(name="<search term>")
```

Returns array of matching programs. Each result has: `id`, `name`, `type`, `channel`,
`status`, `folder`, `workspace`.

If no results, fall back to:

```
get_program_by_name(name="<exact name>")
```

**Output needed:** Program `id` (integer).

### 2. Get Full Program Metadata

```
get_program_by_id(id=<programId>)
```

Returns the complete program record. Key fields:

| API Field | Document Section | Document Field |
|---|---|---|
| `name` | 1. Overview | Program Name |
| `type` | 1. Overview | Program Type |
| `channel` | 1. Overview | Channel |
| `description` | 1. Overview | Purpose |
| `status` | 1. Overview | Status |
| `folder.value` | 1. Overview | Folder |
| `folder.folderName` | 1. Overview | Folder (display name) |
| `workspace` | 1. Overview | Workspace |
| `createdAt` | 1. Overview | Created |
| `updatedAt` | 1. Overview | Last Modified |
| `tags[]` | 2. Configuration | Tags |
| `costs[]` | 2. Configuration | Period Cost |
| `sfdcId` | 2. Configuration | SFDC Campaign Sync |
| `sfdcWorkspaceId` | 2. Configuration | SFDC Workspace |

**Tags array format:** `[{ tagType: "Region", tagValue: "North America" }, ...]`
Map each to a row: "Region: North America"

**Costs array format:** `[{ startDate: "2024-01-01", cost: 5000, note: "Q1 budget" }, ...]`
Map each to: "$5,000.00 — Q1 budget (01/01/2024)"

### 3. Get Local Tokens

```
get_tokens_by_folder(id=<programId>, folderType="Program")
```

**Critical:** Always pass `folderType="Program"` explicitly. The default is "Folder"
which will return wrong results or fail silently.

Returns local tokens only (not inherited). Each token has:

| API Field | Document Field |
|---|---|
| `name` | Token Name (display as `{{my.name}}`) |
| `type` | Type |
| `value` | Current Value |

**Type values:** `text`, `rich text`, `date`, `number`, `score`, `sfdc campaign`

### 4. Browse Smart Campaigns

```
browse_smart_campaigns(folder={id: <programId>, type: "Program"})
```

Returns list of smart campaigns. Each has: `id`, `name`, `type`, `status`, `isActive`,
`isRequestable`, `createdAt`, `updatedAt`.

Note: `maxReturn` defaults to 20. If the program might have more than 20 smart campaigns,
paginate using `offset`.

### 5. Get Smart Campaign Details (per campaign)

For each smart campaign from step 4:

```
get_smart_campaign_by_id(id=<campaignId>, includeFlowSteps=true)
```

This returns the campaign metadata plus **flow steps** — the sequence of actions the
campaign performs. Flow step data includes:

| Field | Maps to |
|---|---|
| Flow step action name | Flow Steps table — Action Name column |
| Flow step parameters/values | Flow Steps table — Details column |
| Choice steps (conditions + actions) | Flow Steps table — indented under parent step |
| Wait steps (duration) | Flow Steps table — "Wait — [duration]" |
| Step order/index | Flow Steps table — Step Number column |

### 6. Get Smart List Rules (per campaign)

```
get_smart_list_by_campaign_id(smartCampaignId=<campaignId>, includeRules=true)
```

Returns the smart list with all triggers and filters. Rule data includes:

| Field | Maps to |
|---|---|
| Rule name | Smart List table — Rule Name column |
| Rule type (trigger vs filter) | Smart List table — Type column |
| Operator | Smart List table — Operator + Values column |
| Values / constraints | Smart List table — Operator + Values column |
| Filter logic (AND/OR/Advanced) | Smart List table — Logic row |

### 7. Get Scheduled Runs (batch campaigns only)

```
get_smart_campaign_scheduled_runs(campaignId=<campaignId>)
```

Only call this for batch-type campaigns. Returns upcoming scheduled run times.

### 8. Browse Emails

```
browse_emails2(folder={id: <programId>, type: "Program"})
```

Returns list of emails. Each has: `id`, `name`, `status`, `folder`, `createdAt`, `updatedAt`.

### 9. Get Email Content (per email)

```
get_email_content(id=<emailId>)
```

Returns content sections including subject line, from name, from email, reply-to, and
all editable content sections with their HTML/text values.

Also useful for health checks:
- Scan content for `{{my.*}}` patterns to detect token references (for HC-12)
- Check for broken token references

### 10. Browse Forms, Lists, and Other Assets

```
get_folder_content(id=<programId>)
```

Returns all assets in the program folder. Use this to discover landing pages, forms,
reports, and other asset types not covered by specific browse endpoints.

For each form found:

```
get_form_by_id(id=<formId>)
get_form_fields(id=<formId>)
```

Form fields return: `fieldId`, `label`, `dataType`, `required`, `formPrefill`,
`validationMessage`, `hintText`, `maxLength`.

For smart lists and static lists:

```
browse_smart_lists(folder={id: <programId>, type: "Program"})
browse_lists(folder={id: <programId>, type: "Program"})
```

---

## Data Normalization Rules

Apply these transformations when mapping API data to document fields:

| Data Type | Transformation | Example |
|---|---|---|
| Dates (ISO 8601) | Format as MM/DD/YYYY | `2024-03-15T10:30:00Z` → "03/15/2024" |
| Booleans | "Yes" / "No" | `true` → "Yes" |
| Null / missing | Italic gray *"Not set"* | `null` → *"Not set"* |
| Empty string | Italic gray *"Empty"* | `""` → *"Empty"* |
| Long text (>200 chars) | Truncate with "..." in tables | "Lorem ipsum dolor..." |
| Rich text token values | Strip HTML tags, append "(rich text)" | `<p><strong>Hello</strong></p>` → "Hello (rich text)" |
| Cost values | Format as $X,XXX.XX | `5000` → "$5,000.00" |
| Arrays (tags, costs) | One item per line or row | See section-specific notes |

### HTML Stripping for Rich Text

When displaying rich text token values in the token table, strip all HTML tags to show
plain text. Keep the text content, remove `<p>`, `<strong>`, `<em>`, `<a>`, `<br>`,
`<div>`, `<span>`, etc. Add "(rich text)" as an italic gray note after the value.

If the stripped text exceeds 200 characters, truncate and add "...".

---

## Rate Limit Awareness

Marketo enforces:
- **100 calls per 20 seconds**
- **50,000 calls per day**
- **10 concurrent connections**

For a typical program with 5 smart campaigns and 3 emails, you will make approximately:
- 1 program detail call
- 1 token call
- 1 browse smart campaigns call
- 5 smart campaign detail calls (with flow steps)
- 5 smart list calls (with rules)
- 1-5 scheduled runs calls (batch only)
- 1 browse emails call
- 3 email content calls
- 1 folder content call
- Variable form/list calls

Total: ~20-30 calls. Well within rate limits.

For large programs (20+ smart campaigns), the detail calls alone could approach
the 100/20s limit. In that case, batch your calls in groups of 10 and allow a brief
pause between groups.

---

## Fields NOT Available via These Tools

Some documentation fields cannot be populated from the MCP tools used here:

| Field | Why unavailable | Handling |
|---|---|---|
| Program member count | Requires Lead Database API with pagination | Show placeholder or omit |
| Success count/rate | Requires aggregation across member statuses | Show placeholder |
| Email open/click rates | Requires Email Performance Report API | Show placeholder |
| Engagement scores | Requires separate engagement program API | Show placeholder |
| Rendered email previews | No screenshot API | Omit — not a table field |

For Section 6 (Performance Snapshot), note: "Performance metrics require separate
Marketo reporting. Review Program Analyzer or the Email Performance Report in Marketo
for engagement data."

---

## Tool Availability Notes

If a direct Marketo MCP tool is not available (returns an error or is not connected),
fall back to the allGood wrappers where possible:

| Direct Tool | allGood Fallback | Limitation |
|---|---|---|
| `get_program_by_id` | `marketo_get_program_details(programId=<id>)` | May not include tags/costs |
| `get_tokens_by_folder` | `marketo_get_program_tokens(programId=<id>)` | Same data |
| `browse_smart_campaigns` | None — use `get_folder_content` | Less structured |
| `get_smart_campaign_by_id` | None | Flow steps only via direct tool |
| `get_smart_list_by_campaign_id` | None | Rules only via direct tool |
| `get_email_content` | `marketo_get_email_details(programId=<id>)` | May return all emails at once |

If smart campaign detail tools are unavailable, document the campaigns by name/type/status
only and note: "Smart campaign details (flow steps, smart list criteria) require direct
Marketo MCP connection — not available in this session."
