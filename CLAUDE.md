# allgood-marketplace

Claude Code plugin marketplace for marketing ops skills built by allGood.

## Project Structure

```
plugins/allgood-plugin/           # The plugin
  .claude-plugin/plugin.json      # Plugin manifest (version bumped by CI — do NOT manually edit version)
  skills/<skill-name>/
    SKILL.md                      # Skill definition (prompt-based)
    references/                   # Supporting docs the skill reads at runtime
    assets/                       # Images, logos
    scripts/                      # Python scripts (marketo-template-parser only)
scripts/package-skill.sh          # Packages a skill dir into a .skill zip
.github/workflows/
  release.yml                     # Tags -> version bump -> package -> attach to release
  package-skills.yml              # CI packaging
```

## Skills

| Skill | Type |
|-------|------|
| `mary-email-performance` | Prompt-only (DOCX report from Marketo CSV) |
| `mary-email-brief` | Prompt-only (campaign briefing DOCX) |
| `marketo-template-parser` | Prompt + Python scripts (HTML template audit) |
| `marketo-tokens` | Prompt-only (Marketo token CRUD via MCP) |

## Conventions

- Skills are prompt-based by default. Only add scripts when a skill genuinely needs programmatic parsing.
- Each skill must have a `SKILL.md` at its root — the packager uses this to detect valid skills.
- Shared logos: `mary-logo.png` (213KB), `allgood-logo.png` (11KB) — reuse from existing skill assets, don't duplicate.
- Brand color: `#dc4393` (pink).
- `plugin.json` version is managed by the release workflow. Never bump it manually.

## Adding a New Skill

1. Create `plugins/allgood-plugin/skills/<skill-name>/SKILL.md`
2. Add `references/` for any supporting docs the skill needs
3. Add `assets/` for images (symlink or copy shared logos)
4. Test locally: `./scripts/package-skill.sh plugins/allgood-plugin/skills/<skill-name>`
5. Update `README.md` with the new skill row

## Working with Python Scripts (marketo-template-parser)

- Python deps in `requirements.txt`, setup via `setup.sh`
- Shared utils in `scripts/parser_utils.py`
- `__pycache__/` and `.claude/` are excluded from `.skill` packages

## Pre-commit Checklist

Before every commit, run:

- [ ] `claude plugin validate .` — validates plugin structure and skill definitions
