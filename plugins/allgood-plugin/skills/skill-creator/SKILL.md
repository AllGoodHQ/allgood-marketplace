---
name: skill-creator
description: >
  Use this skill whenever a user wants to create a new Claude Code skill for the allGood
  marketplace. Triggers include: "create a new skill", "build a skill", "add a skill to
  the marketplace", "I want to make a skill", "help me write a skill", or any request to
  package Claude expertise into a reusable SKILL.md for the plugin. Always use this skill
  when the user is trying to define a repeatable workflow that others could install and run.
---

# Skill Creator

This skill guides you through building a new Claude Code skill for the allGood marketplace.
A skill is a SKILL.md file that tells Claude exactly how to execute a repeatable workflow —
with step-by-step instructions, reference files, and validation checklists.

---

## User Request

The user has requested: $ARGUMENTS

Adapt based on what the user provided:
- **Skill idea described** (e.g. "a skill that builds UTM reports") → start with Step 1,
  use their description as the seed
- **Existing workflow to package** (e.g. "I already do this manually, help me wrap it") →
  interview them about their current process in Step 1, then proceed
- **No details given** → run the full default interview (all of Step 1) before writing
  anything

Always complete Steps 1 and 2 before writing any files.

---

## How to Use This Skill

This skill has one reference file. Load it at the right step.

| Reference File | Load When |
|---|---|
| `references/skill-spec.md` | Step 3 — when writing the SKILL.md |

---

## Step 1: Interview the User

Before writing anything, understand what the skill should do. Ask these questions — all
at once in a single message so the user can answer in one go:

1. **What does this skill do?** In one sentence, what workflow does it automate or assist
   with? (e.g. "It analyzes a CSV and builds a UTM audit report")
2. **What triggers it?** What would a user say to invoke this skill? List 3–5 example
   phrases they might use.
3. **What inputs does it need?** Files, data, a campaign name, a URL? What does the user
   have to provide before the skill can run?
4. **What does it produce?** A DOCX? A JSON file? A Slack message draft? A structured
   answer in chat? Be specific about the output format.
5. **What are the steps?** Walk through the workflow from start to finish. Even rough notes
   are fine — you'll clean them up.
6. **Are there any reference materials?** Benchmarks, format specs, a style guide,
   API docs? List them. These become the skill's `references/` files.
7. **What can go wrong?** What errors or edge cases should the skill handle?
8. **What tools or libraries does it use?** Python, pandas, docx, MCP tools, bash scripts?

If the user provides partial answers, follow up only on what's missing. Don't ask questions
that are already answered.

---

## Step 2: Design the Skill Structure

Once you have the answers, design the skill before writing any files.

### 2a. Name the Skill

Pick a short, lowercase, hyphenated name (e.g. `utm-auditor`, `campaign-namer`,
`deliverability-checker`). It should describe the output, not the process.

### 2b. Write the Trigger Description

Draft the `description:` field for the SKILL.md front matter. It must:
- Start with "Use this skill whenever..."
- List at least 4 specific trigger phrases in quotes
- End with a general catch-all rule

### 2c. Map the Steps

Break the workflow into 3–6 numbered steps. For each step, decide:
- What does this step do?
- What reference file (if any) should Claude load here?
- What should Claude print or produce at the end of this step?
- Is there a user confirmation needed before proceeding?

### 2d. Define Reference Files

For each reference file the skill needs, decide:
- What information does it contain?
- When should it be loaded (which step)?
- Will you create placeholder content now, or does the user need to supply it?

### 2e. Draft the Validation Checklist

List 8–15 specific checkboxes Claude should verify before delivering the output.
Make them concrete and testable, not vague ("All required fields are present" not
"Output looks good").

Present the full design to the user as a structured summary:

```
Skill name: <name>
Trigger description: <draft>

Steps:
  Step 0: <name> — <what it does>
  Step 1: <name> — <what it does>
  ...

Reference files:
  references/<filename>.md — <what it contains> — loaded at Step N

Validation checklist:
  - [ ] <item>
  - [ ] <item>
  ...
```

Ask the user to confirm or adjust before proceeding to Step 3.

---

## Step 3: Write the Skill Files

**Read `references/skill-spec.md` now.** Follow the format specification exactly.

### 3a. Create the Directory Structure

```
plugins/allgood-plugin/skills/<skill-name>/
  SKILL.md
  references/          (if the skill has reference files)
```

Create the skill directory and write the SKILL.md based on the confirmed design from
Step 2.

### 3b. Write Reference File Stubs

For each reference file defined in the design:
- If the user provided content → write it out fully
- If it's a placeholder → write a stub with clear section headers and a note that the
  user needs to fill in the details. Use this format at the top:

```
<!-- STUB: This file needs to be filled in before the skill is usable.
     See the instructions below for what to include. -->
```

### 3c. Update the README

Add a row for the new skill in the root `README.md` skills table:

```markdown
| **<Skill Display Name>** | <One-sentence description of what it does.> | [![Download](https://img.shields.io/github/v/release/AllGoodHQ/allgood-marketplace?label=download&style=flat-square)](https://github.com/AllGoodHQ/allgood-marketplace/releases/latest/download/<skill-name>.skill) |
```

---

## Step 4: Validation Checklist

After writing all files, verify every item below. Fix any failures before delivering.

- [ ] SKILL.md front matter has `name:` and `description:` fields
- [ ] `description:` starts with "Use this skill whenever..."
- [ ] `description:` includes at least 4 trigger phrases in quotes
- [ ] SKILL.md has a "User Request" section with `$ARGUMENTS`
- [ ] Every step has a clear heading and concrete actions
- [ ] Reference files are listed in a load-order table
- [ ] Each step specifies *when* to load each reference file (not "load all upfront")
- [ ] A validation checklist exists with at least 8 specific, testable items
- [ ] All referenced files exist on disk (no broken references)
- [ ] Stub files have the STUB notice at the top
- [ ] Skill directory name matches the `name:` field in front matter
- [ ] README.md row added with correct skill name and download URL
- [ ] SKILL.md does not exceed ~400 lines (move detail to reference files if needed)

If any check fails, fix it and re-run the checklist before delivering.

---

## Wrap Up

Once all files are written and validated, summarize for the user:

```
Skill created: <skill-name>
Location: plugins/allgood-plugin/skills/<skill-name>/

Files written:
  SKILL.md              — main skill prompt
  references/<file>.md  — <what it contains>   [STUB / complete]
  ...

Next steps:
  1. Fill in any STUB reference files with your actual content
  2. Test the skill by invoking it with a real request
  3. Commit and open a PR to add it to the marketplace
```
