# Marketo Templates — High-Impact Use Cases

Tracker for the capabilities the `marketo-parser` skill should support, now or later. Each entry records what the capability is, why it's in demand, how it maps to current scripts/references, and whether the skill covers it today.

**Coverage legend**

- **covered** — the current SKILL.md handles this end-to-end
- **partial** — the skill handles part of it; gaps noted
- **future** — not in this skill yet; capture requirements for a follow-up

---

## Coverage summary

| # | Use case | Coverage |
|---|---|---|
| 1 | Validation with root causes | partial |
| 2 | Cross-client rendering lint | covered |
| 3 | Marketofying external HTML | future |
| 4 | Module/container structure enforcement | partial |
| 5 | Silent code corruption detection | future |
| 6 | Template-email propagation impact | future |
| 7 | Accessibility / WCAG linting | covered (basics) / partial (full WCAG AA) |
| 8 | Template size + Gmail clipping | partial |

**Next most valuable additions:**
- **#3 (Marketofying)** — highest-frequency entry point, no existing tooling, highest-leverage automation per the research
- **#1 + #4 gaps (structural validation)** — additive rules in `validate.py` that close the top "Invalid Module" debugging loop
- **#8 per-module weight breakdown** — small, composes with existing scripts, directly prevents tracking-pixel loss

---

## 1. Validation that explains what's wrong

- **Demand signal:** Marketo's native validator returns vague messages like `Error: Invalid Module: #yourModuleId` with no line numbers and no root cause. Users describe spending **3–4 hours per template** chasing single-character casing mismatches, blank lines above `<html>`, or modules that aren't direct children of the container. This is the most-cited pain point in community forums.
- **API/script feasibility:** Pure DOM parsing — no API needed. BeautifulSoup walks the tree once and surfaces structural issues with line numbers.
- **Coverage:** **partial**.
  - **What `validate.py` catches today (all with line numbers):** missing/multiple `mktoContainer`, duplicate IDs, invalid ID format, missing `mktoName` on modules and editable elements, `{{my.token}}` in HTML attributes outside editable regions; warnings for case-sensitive attribute names, unused variables, missing defaults, non-camelCase variable IDs, URL variables missing `https://` protocol.
  - **Gaps the research calls out:**
    - Parent-child element type compatibility (`<table class="mktoContainer">` requires `<tr class="mktoModule">` children, `<td class="mktoContainer">` requires `<table class="mktoModule">` children)
    - Nested module detection (the #1 cause of `Invalid Module` per community docs)
    - Cross-check `<meta>` variable declarations against `${variableId}` references with case-sensitive matching, to surface "no variable with this ID declared" before Marketo does
    - Format mismatches for typed variables (`mktoColor` requires HEX not RGB; `mktoNumber` bounds)
    - Blank line above `<html>` tag (silently breaks `mktEditable` parsing)
    - Variables declared with `mktoModuleScope="false"` mistakenly assumed to be per-module
- **Design notes:** Adding the parent-child type check is high-leverage and self-contained. The case-sensitive variable cross-check requires touching `parser_utils` to thread declarations through to `validate.py`. Surface gaps as separate validation rule IDs so users can filter (e.g., `--rule structure`).

---

## 2. Cross-client rendering issues caught before send

- **Demand signal:** Outlook desktop uses Microsoft Word as its rendering engine (ignores `max-width`, `flexbox`, `grid`, mishandles `line-height` on images). Gmail clips at ~102KB and strips `<style>` tags from the clipped portion — silently hiding tracking pixels and killing open-rate data. Dark mode forces color inversions that override template CSS. Users currently rely on Litmus / Email on Acid round-trips to discover these issues post-build.
- **API/script feasibility:** Pure HTML lint. No API needed.
- **Coverage:** **covered**.
  - **What `lint_email.py` catches today (~30 rules across 10 categories):** missing DOCTYPE / lang / charset; img alt text / dimensions / SVG-in-Outlook / HTTP; broken/javascript/no-text links; layout tables missing `role="presentation"`; deeply nested tables; inline-style anti-patterns Outlook ignores; font fallback / minimum size; **Gmail 102KB clip warning, 8KB style block cap, `<style>` in body, `background-image` in style block, attribute selectors stripped**; **MSO padding-on-`<a>`, image sizing, VML xmlns, `<button>` element**; **dark mode bg-without-text-color, pure black/white inversion, missing `@media (prefers-color-scheme)`, PNG without dark-mode fallback**.
  - **Gaps:** Gmail iOS app's separate ~20KB clip threshold not flagged. Per-module weight breakdown when a template fails SIZE-001 — currently you know "it's too big" but not "module X is the heaviest." See use case #8.
- **Design notes:** Run `lint_email.py --category outlook gmail darkmode` for client-specific reports. Pair with `references/email-rendering-rules.md` to explain *why* each rule fires.

---

## 3. "Marketofying" external HTML

- **Demand signal:** Every team that designs externally — BEE Free, MJML, hand-coded HTML — has to convert that output into valid Email 2.0 syntax (containers, modules, editable regions, variables) by hand. It's the highest-frequency entry point into the Marketo template lifecycle and a multi-hour fragile process. The element-type rules (table→tr, td→table) trip up developers repeatedly. MJML's div-based output is fundamentally incompatible with Marketo's table-based requirement, forcing significant post-compile rework.
- **API/script feasibility:** Pure transformation. Parse incoming HTML, identify logical content sections, apply `mktoContainer` / `mktoModule` / `mktoText` / `mktoImg` classes, generate `<meta>` variable declarations. No API needed.
- **Coverage:** **future**. The current skill is read/validate/lint — there is no generator or converter. Closest existing capability: `get_module.py` returns an existing module's HTML, which a user could copy as a *manual* pattern.
- **Open questions:**
  - Scope: just the structural wrapping (containers + modules), or also infer editable regions and variables from semantic cues (h1 → `mktoText`, img → `mktoImg`)?
  - Input shapes: BEE Free export, MJML output, raw HTML — handle all, or start with one?
  - Interactive vs one-shot? A `marketofy.py` that proposes a converted template and a diff for the user to review-and-approve seems safest.
- **Design notes:** This is the highest-leverage automation opportunity per the research. It sits at the start of every template's lifecycle and currently has no tooling.

---

## 4. Module and container structure enforcement

- **Demand signal:** Three hard constraints cause the majority of `Invalid Module` failures: only one container per template, containers can only contain modules (no spacer `<tr>`s, no wrapper `<div>`s), no nested modules. `mktoModuleScope` defaulting to `false` (global) when omitted surprises users — duplicating a module makes all instances share the same variable values. There's also a documented `mktoImg` class-doubling bug.
- **API/script feasibility:** Pure DOM walk. No API needed.
- **Coverage:** **partial**.
  - **Today:** `validate.py` enforces single container, unique IDs, `mktoName` presence. `references/marketo-template-reference.md` and the SKILL.md "Critical Constraints" table document the rules, but enforcement is incomplete.
  - **Gaps:**
    - **Container-children check** — every direct child of `mktoContainer` must be a module (currently unchecked)
    - **Nested-module detection** — modules inside modules silently fail validation in Marketo (currently unchecked)
    - **Parent-child element type matching** — see use case #1
    - **`mktoModuleScope` warnings** — surface when scope is omitted (defaults to global) on a variable that looks per-instance (e.g., color variable in a duplicated module)
    - **`mktoImg` class-doubling** — detect templates likely to trigger the documented bug
- **Design notes:** Most of these are additive checks in `validate.py`. Worth adding all at once under a new rule category to keep the change cohesive.

---

## 5. Silent code corruption detection

- **Demand signal:** Marketo's editor actively modifies template code in damaging ways — stripping `<!--[if mso]>` conditional comments during approval (broke responsive layouts platform-wide; required a manual per-instance fix), rewriting DOCTYPEs, injecting stray `&nbsp;` and empty `<p>` tags, **silently truncating templates on certain UTF-8 characters**, and treating `###` as a Velocity comment delimiter (strips everything after it on that line, *at send time only* — previews look fine).
- **API/script feasibility:** Pre-save lint pass. No API needed; the script just inspects the source for risky patterns.
- **Coverage:** **future**. None of these are checked today.
- **Open questions:**
  - Where does this live — extend `validate.py` (it's about template integrity), or extend `lint_email.py` (it's about silent failures)? Probably `validate.py` since it's Marketo-specific.
  - Conditional-comment stripping: detect their *presence* and warn that older Marketo instances may strip them, or actually verify the instance's current behavior?
  - UTF-8 truncation chars: which specific characters? Need to compile the list from community reports.
  - Velocity `###`: easy to flag — any `#` followed by two more `#` outside an editable region.
- **Design notes:** This is "prevent the next disaster" tooling. Low frequency, but when these issues hit they take down whole campaigns. Worth a dedicated rule category.

---

## 6. Template-email propagation impact analysis

- **Demand signal:** Module changes never propagate to existing emails. Element and variable changes also don't propagate. Only hard-coded content *outside* editable regions propagates, and only after re-approving both the template and each affected email. **Approving any template change forces every dependent email to draft status** — potentially hundreds of assets requiring manual re-approval. Teams want to know, *before* they hit save, what they're about to break.
- **API/script feasibility:** Two parts: (a) diff two template versions and classify changes as propagating vs non-propagating; (b) find the emails using a given template via MCP. Part (a) is pure local; part (b) needs the MCP.
- **Coverage:** **future**. The current skill produces `generate_registry.py` output that *could* be diffed externally, but has no built-in diff. The MCP tools don't expose a "find emails by template ID" endpoint in the catalog (only `get_email_by_id` etc.) — likely needs the broader Marketo Asset API (`/asset/v1/email/byTemplate.json` or similar).
- **Open questions:**
  - Diff granularity: structural (modules added/removed) vs semantic (variable defaults changed) vs raw HTML?
  - Output format: change-classified report (propagating / non-propagating / breaking) + count of affected emails?
  - Does the MCP / allGood MCP expose an emails-by-template endpoint? If not, this stays partial-by-design.
- **Design notes:** Even part (a) standalone — `diff_templates.py <old> <new>` returning a propagation-classified report — would be high-value without needing MCP. Build that first.

---

## 7. Accessibility and compliance linting

- **Demand signal:** Adobe's own 2020 Accessibility Conformance Report rates Marketo as "Does Not Support" for WCAG Level A criteria including non-text content (1.1.1), info and relationships (1.3.1), and keyboard accessibility (2.1.1). The platform provides no enforcement. Layout tables required by `mktoContainer`/`mktoModule` cause screen readers to announce "Table with X columns and Y rows" unless `role="presentation"` is added manually. `mktoImg` doesn't require alt text. `mktoText` can wrap any element with no semantic-structure check.
- **API/script feasibility:** Pure HTML lint.
- **Coverage:** **covered** for the basics, **partial** for the full WCAG 2.1 AA picture.
  - **Today:** `lint_email.py --category accessibility` flags missing alt text (IMG-001), layout tables without `role="presentation"` (TBL-001), `<a>` tags with no visible text (LINK-004), font sizes below 14px (TYPO-002), missing `lang` on `<html>` (STRUCT-002), and a few more in the accessibility category.
  - **Gaps:**
    - **Heading hierarchy** check (`<h1>` → `<h2>` → `<h3>` order, no skips)
    - **Color contrast ratios** (WCAG AA requires 4.5:1 for normal text, 3:1 for large text — this needs computing actual contrast from inline styles)
    - **Landmark roles** (`role="banner"`, `role="contentinfo"` for header/footer)
    - **Plain-text version review** — the auto-generated plain text is described as "not great" by accessibility consultants
- **Design notes:** Heading hierarchy and color contrast are the two highest-impact additions. Contrast is the heavier lift (need to resolve background color through nested elements).

---

## 8. Template size and Gmail-clipping risk

- **Demand signal:** Module-heavy "master templates" with desktop/mobile dual blocks easily exceed Gmail's 102KB clip threshold. Clipping hides the tracking pixel — **open rates silently stop being recorded** for clipped sends. Each module adds structural overhead (table boilerplate, inline styles, conditional comments). Redundant inline CSS — every element carrying its own `style` attribute, often with the same font-family declaration repeated 50 times — is a major contributor.
- **API/script feasibility:** Pure size accounting on the source. No API needed.
- **Coverage:** **partial**.
  - **Today:** `lint_email.py` SIZE-001 errors when total HTML exceeds 102KB; SIZE-002 warns when close to the limit. GMAIL-001 catches `<style>` blocks in `<body>`. GMAIL-002 catches `<style>` blocks over 8,192 chars (Gmail strips them entirely).
  - **Gaps:**
    - **Per-module weight breakdown** — when a template fails SIZE-001, the user knows it's too big but not *which module* is the heaviest. Could be a `--breakdown` flag on `lint_email.py` or a new `module_weights.py`
    - **Redundant inline CSS detection** — flag duplicated style declarations across many elements (e.g., `font-family: Arial, sans-serif` repeated 50 times → suggest moving to a class or container style)
    - **Dead-code from desktop/mobile dual blocks** — measure how much weight comes from `display:none` or class-toggled hidden content
    - **Gmail iOS ~20KB threshold** — separate, lower clip on mobile Gmail; not currently flagged
- **Design notes:** Per-module weight breakdown is the most useful next step — composes well with existing `get_module.py` output. Could be added as a new script `module_weights.py` or as `get_module.py --weight`.

