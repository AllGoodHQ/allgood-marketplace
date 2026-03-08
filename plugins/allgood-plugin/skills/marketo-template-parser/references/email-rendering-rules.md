# Email HTML Rendering Rules Reference

Condensed reference for understanding lint_email.py rules. Organized by client/category.

## Outlook (Windows Desktop — Word Engine)

Outlook 2007-2019 and Office 365 desktop use Microsoft Word to render HTML. This is the most restrictive major client.

**What breaks:**
- `float`, `position`, `display:flex/grid` — completely ignored, use tables for layout
- `padding` on `<a>`, `<img>`, `<div>`, `<p>`, `<span>` — ignored; only works on `<td>`
- `max-width` — ignored; content stretches to full viewport width
- `margin:auto` — does not center elements; use `align="center"`
- CSS `width`/`height` on `<img>` — ignored; must use HTML attributes
- `background-image` in CSS — not rendered; requires VML (`<v:rect>` with `<v:fill>`)
- `border-radius`, `box-shadow`, `opacity`, `transform`, CSS animations — unsupported
- `@media` queries — completely ignored
- `@font-face` — unsupported; falls back to system fonts (Times New Roman if stack is wrong)
- `!important` in inline styles — entire declaration ignored (only works in `<style>` blocks)
- `<button>` elements — broken/non-clickable; use styled `<a>` inside `<td>` with padding

**Required workarounds:**
- Ghost tables: `<!--[if mso]><table width="600" style="width:600px;"><tr><td><![endif]-->` around `max-width` containers
- VML for background images: `<v:rect>` with `xmlns:v="urn:schemas-microsoft-com:vml"` on `<html>`
- HTML attributes on images: `<img width="600" height="400">` not just CSS
- MSO CSS resets: `mso-table-lspace:0pt; mso-table-rspace:0pt` on tables
- Use `style="width:600px"` (CSS) not `width="600"` (HTML attr) on ghost tables for DPI scaling

**Transition note:** Microsoft ends Word-based Outlook support Oct 2026. New Outlook uses Chromium. But enterprise adoption won't catch up until 2028-2029, so maintain both for now.

## Gmail

~31% global market share. Acts as an aggressive sanitization engine.

**Style block rules:**
- `<style>` must be in `<head>` — body styles stripped
- 8,192 character limit per `<style>` block — exceeding causes entire block removal plus all subsequent blocks
- `background-image: url()` inside any `<style>` rule — Gmail strips the entire block
- Nested `@` declarations (`@media` inside `@supports`) — triggers full block stripping
- One CSS syntax error — can cause entire block removal
- Attribute selectors (`div[class="x"]`) — stripped; use class selectors (`.x`)

**Size limit:** 102KB total HTML — exceeding causes Gmail to clip the message, hiding footers, unsubscribe links, and tracking pixels.

**GANGA (Gmail app with non-Gmail accounts):** Strips ALL `<style>` blocks. Critical styles must be inlined.

**Dark mode:** Gmail does NOT support `@media (prefers-color-scheme: dark)`. Gmail Desktop: no changes. Gmail Android: partial inversion. Gmail iOS: full inversion. No reliable prevention — design defensively.

**Link override:** Gmail turns links blue. Fix with `u + #body a { color: inherit !important; }` and `<body id="body">`.

## Apple Mail / iOS Mail

Best CSS support of any client (283/303 features on caniemail.com). WebKit engine supports flexbox, grid, animations, web fonts, CSS variables.

**Dark mode is opt-in:**
- Without meta tags: colors unchanged in dark mode (safest default)
- With `<meta name="color-scheme" content="light dark">` but no CSS: partial inversion applied
- With meta tag + `@media (prefers-color-scheme: dark)` CSS: full developer control

**Auto-linking:** iOS auto-links phone numbers, addresses, dates. Prevent with:
- `<meta name="format-detection" content="telephone=no">`
- `a[x-apple-data-detectors] { color: inherit !important; text-decoration: none !important; }`

**Required meta:** `<meta name="x-apple-disable-message-reformatting">` prevents iOS 10+ scaling artifacts.

## Dark Mode Matrix

| Behavior | Clients |
|----------|---------|
| No change | Apple Mail (no meta), Gmail Desktop, Yahoo Desktop |
| Partial invert | Outlook.com, Outlook mobile, Gmail Android, O365 Mac |
| Full invert | Gmail iOS, Outlook 2021 Windows, O365 Windows, Windows Mail |
| Supports prefers-color-scheme | Apple Mail, Samsung Email 6.1+, Thunderbird 68.4+ |

**Defensive rules:**
- Avoid pure `#FFFFFF` and `#000000` — use `#FAFAFA` and `#111111` (pure values trigger aggressive inversion)
- Always set both `background-color` AND `color` on every container
- Transparent PNG logos need white stroke/glow or image-swap for dark mode
- `background-image: linear-gradient(#color, #color)` survives Gmail inversion (Gmail modifies `background-color` but not `background-image`)

## Accessibility (WCAG 2.1 AA)

99.89% of emails fail accessibility checks (Email Markup Consortium 2025). Top issues:

- **96.37% missing `lang` on `<html>`** — screen readers mispronounce content
- **`role="presentation"` on layout tables** — without it, screen readers announce "table with X columns and Y rows"
- **`alt` on every `<img>`** — descriptive for content images, `alt=""` for decorative. Never omit entirely (screen reader reads filename)
- **Contrast: 4.5:1** for normal text, 3:1 for large text (>=18px or >=14px bold)
- **Links must be underlined** — color alone insufficient (color-blind users)
- **Min 14px body text**, 16px recommended. Line-height >= 1.5x font size
- **44x44px minimum touch targets** for CTA buttons
- **Sequential headings** — h1 then h2 then h3, no skipping levels
- **No `title` on interactive elements** — screen readers read both title and text, creating duplication

## Responsive Patterns

**Hybrid/spongy is the gold standard** — works without media queries:
1. Base: fluid CSS (`width:100%; max-width:600px; display:inline-block`)
2. Outlook layer: ghost tables in MSO conditionals for fixed width
3. Enhancement: `@media` queries for fine-tuning on supporting clients

**Media query support:**
- Full: Apple Mail, Thunderbird
- Partial: Gmail iOS/Android (native), Outlook.com, Outlook macOS, Yahoo, Samsung
- None: Gmail Desktop Webmail, Outlook Windows 2007-2019, Windows Mail

**Critical:** Media query styles MUST use `!important` to override inline styles. One misplaced bracket causes Gmail to ignore all embedded styles.
