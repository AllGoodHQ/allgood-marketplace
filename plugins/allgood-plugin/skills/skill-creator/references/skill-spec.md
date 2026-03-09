# Skill Specification Format

This document defines the exact format and conventions for writing allGood marketplace
skills. Follow it precisely when writing a new SKILL.md.

---

## File Layout

```
plugins/allgood-plugin/skills/<skill-name>/
  SKILL.md                     ← required
  references/                  ← optional, one file per major reference topic
    <topic>.md
  assets/                      ← optional, images and static files
    <file>
  scripts/                     ← optional, Python or shell scripts
    <script>.py
```

The skill directory name must be lowercase, hyphenated, and match the `name:` field in
the SKILL.md front matter exactly.

---

## SKILL.md Structure

Every SKILL.md must follow this structure in order:

### 1. Front Matter

```yaml
---
name: <skill-name>
description: >
  Use this skill whenever <trigger condition>. Triggers include: "<phrase 1>",
  "<phrase 2>", "<phrase 3>", "<phrase 4>". Always use this skill when
  <catch-all rule>.
---
```

Rules:
- `name` must match the directory name exactly
- `description` is what Claude uses to decide when to load this skill
- The description must start with "Use this skill whenever"
- Include 4+ specific trigger phrases in double quotes
- End with a general catch-all rule ("Always use this skill when...")
- Keep the description under 150 words

### 2. Title and Overview

```markdown
# <Skill Display Name>

<2–4 sentence overview of what this skill does, why it exists, and what it produces.>
```

### 3. User Request Section

Always include this section immediately after the overview:

```markdown
## User Request

The user has requested: $ARGUMENTS

Adapt the output based on what the user asked:
- **<Variation 1>** → <what to do differently>
- **<Variation 2>** → <what to do differently>
- **No specific ask / generic request** → run the full default workflow (all steps)

Always complete Step 0 (<name>) and Step 1 (<name>) regardless of the request.
The adaptation applies to Step N onwards.
```

`$ARGUMENTS` is replaced at runtime with whatever the user typed after the skill name.

### 4. Reference File Load Table

If the skill has reference files, list them here:

```markdown
## How to Use This Skill

This skill has N reference file(s). Load them at the right step — don't load all at once.

| Reference File | Load When |
|---|---|
| `references/<file>.md` | Step N — when doing <action> |
```

If there are no reference files, omit this section.

### 5. Steps

Number steps starting from 0. Step 0 is always the "setup" or "intake" step.

```markdown
## Step 0: <Step Name>

<What Claude should do in this step. Be concrete.>

### Sub-section (if needed)

<Detail.>
```

Step conventions:
- Each step should produce something visible (output, confirmation, a file)
- If a step requires loading a reference file, say so explicitly at the top of the step
- If a step requires user confirmation before proceeding, say "Ask the user to confirm
  before proceeding" at the end
- Steps should not exceed ~50 lines; move detail into reference files
- The last step before the checklist is always the "Build the output" step

### 6. Validation Checklist

Always the second-to-last section:

```markdown
## Step N: Validation Checklist

After generating the output, run through every item below. Fix any failures before delivering.

- [ ] <Specific, testable check>
- [ ] <Specific, testable check>
...
```

Rules:
- At least 8 items
- Each item must be specific and testable — not vague
- Order: correctness checks first, formatting second, branding/output last
- If a check fails, say "fix it and re-run the checklist before outputting"

### 7. Wrap Up (optional)

Some skills end with a summary section:

```markdown
## Wrap Up

<What Claude should say when done. Include a summary format if the output
has multiple parts.>
```

---

## Writing Style

**Be imperative.** Every instruction is a command to Claude.
- Good: "Extract the campaign name from the user's request"
- Bad: "The campaign name should be extracted"

**Be specific.** Name the exact tool, method, or file.
- Good: "Call `allgood_list_campaigns(name='<campaign name>')`"
- Bad: "Look up the campaign"

**Lazy loading.** Never say "load all reference files at the start." Specify the exact step.
- Good: "**Read `references/benchmarks.md` now.**"
- Bad: "See the reference files for benchmarks"

**Short steps.** If a step is more than ~50 lines, split it or move content to a reference file.

**No hedging.** Don't write "you might want to" or "consider". Just say what to do.

---

## Reference File Format

Reference files contain factual content that would bloat the SKILL.md: lookup tables,
format specs, benchmarks, example outputs, API schemas, etc.

Structure:
- Use Markdown headers (##, ###)
- Lead with a one-line summary of what the file contains
- Include examples wherever possible
- End with a section that addresses the most common edge cases

Reference files should be self-contained — Claude should be able to answer any question
about the topic from the reference file alone, without needing to search elsewhere.

---

## Common Patterns

### Asking for Input

When the skill needs something from the user before it can proceed:

```markdown
Ask the user for:
1. <Thing 1> — why it's needed
2. <Thing 2> — why it's needed

Do NOT proceed to Step N until you have both.
```

### Two-Path Workflows (MCP vs. Manual)

When the skill works differently depending on available tools:

```markdown
### Path A: MCP Tools Available

1. <Step using MCP tool>
2. <Step using MCP tool>

### Path B: No MCP Tools

1. <Manual alternative>
2. <Manual alternative>
```

### Producing a DOCX

Reference the DOCX skill for the full API. In the step:

```markdown
Use the `docx` npm library (see DOCX skill for full technical reference if needed).

Save to `/mnt/user-data/outputs/<output-filename>.docx`.
```

### Writing Python Scripts

When the skill includes Python scripts in `scripts/`:

```markdown
## Prerequisites

Python 3 and <library>. Install with: `pip3 install <library>`
```

### Handling Missing Files or Tools

```markdown
If <file/tool> is missing or unavailable:
- <Fallback action>
- Do NOT proceed until the user confirms the issue is resolved / use the fallback
```

---

## Length Budget

| Section | Recommended Length |
|---|---|
| Front matter | 8–15 lines |
| Overview | 3–5 lines |
| User Request | 8–15 lines |
| Reference load table | 4–8 lines |
| Each step | 15–50 lines |
| Validation checklist | 10–20 lines |
| **Total SKILL.md** | **100–400 lines** |

If a SKILL.md exceeds 400 lines, move detail into reference files.

---

## Naming Conventions

| Thing | Convention | Example |
|---|---|---|
| Skill directory | lowercase-hyphenated | `utm-auditor` |
| `name:` field | same as directory | `utm-auditor` |
| Reference files | lowercase-hyphenated | `benchmark-targets.md` |
| Script files | snake_case.py | `parse_report.py` |
| Output files | `<descriptor>-<type>.<ext>` | `email-performance-report.docx` |
| Asset files | lowercase-hyphenated | `mary-logo.png` |
