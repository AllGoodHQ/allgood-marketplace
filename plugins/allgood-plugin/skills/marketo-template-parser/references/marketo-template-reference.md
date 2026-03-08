# Marketo Email Template 2.0 — Complete Syntax Reference Manual

> **SCOPE:** This document covers **Marketo Email Editor 2.0 template syntax only** — the modular system using `mktoModule`, `mktoContainer`, `mktoText`, `mktoImg`, `mktoSnippet`, `mktoVideo`, and `<meta>` variable declarations. It does **not** cover Landing Page templates, Forms 2.0, or the legacy Email Editor 1.0 (except for differentiation purposes).
>
> **PURPOSE:** Reference-only document supporting: (1) reviewing existing v2.0 templates for correctness, (2) making improvements to v2.0 templates, and (3) answering questions about v2.0 template syntax.
>
> **PRIMARY SOURCE:** [Adobe Marketo Engage — Email Template Syntax](https://experienceleague.adobe.com/en/docs/marketo/using/product-docs/email-marketing/general/email-editor-2/email-template-syntax) (last updated September 2025). Supplemented by Marketo Nation community posts and email development resources.

---

## Critical Constraints (Read First)

| # | Constraint | Consequence if Violated |
|---|-----------|------------------------|
| 1 | **Only ONE `mktoContainer` per template** | Template fails validation; "Invalid Module" error |
| 2 | **Containers can ONLY contain Modules** — no other HTML elements as direct children | "Invalid Module" error; stray `<br>`, comments, or wrapper `<div>` tags trigger this |
| 3 | **Class names are CASE-SENSITIVE** (`mktoText` not `mktotext`) | Element silently ignored by parser; no error thrown |
| 4 | **Custom attribute names are NOT case-sensitive** (`mktoName` = `mktoname`) | Both work; camelCase recommended for consistency |
| 5 | **All `id` values must be unique across the entire template** | Editor crash, random ID suffixes appended, broken CSS references |
| 6 | **IDs: letters, numbers, dash `-`, underscore `_` only; no spaces** | Validation failure |
| 7 | **Module element type must match container element type** | See Container-Module Pairing Rules below |
| 8 | **Modules cannot be nested inside other modules** | "Invalid Module" error |
| 9 | **Marketo syntax does NOT work inside Snippets or Rich Text tokens** | Variables and tokens will not resolve |
| 10 | **`mktoButton` does NOT exist in Email 2.0** — it is a Forms 2.0 class only | N/A; use table-based buttons with `mktoText` + variables |

---

## 1. Version Identification: v1.0 vs v2.0

### 1.1 Definitive v2.0 Markers

A template is classified as Email 2.0 if it contains **any** of these class names:

| Marker | Location | Example |
|--------|----------|---------|
| `mktoContainer` | Body HTML element class | `<table class="mktoContainer" ...>` |
| `mktoModule` | Body HTML element class | `<tr class="mktoModule" ...>` |
| `mktoText` | Body HTML element class | `<div class="mktoText" ...>` |
| `mktoImg` | Body HTML element class | `<div class="mktoImg" ...>` |
| `mktoSnippet` | Body HTML element class | `<div class="mktoSnippet" ...>` |
| `mktoVideo` | Body HTML element class | `<div class="mktoVideo" ...>` |
| `mktoString` / `mktoColor` / `mktoBoolean` / `mktoNumber` / `mktoList` / `mktoHTML` / `mktoImg` (meta) | `<meta>` class in `<head>` | `<meta class="mktoColor" ...>` |

### 1.2 v1.0 Contrast

| Feature | v1.0 | v2.0 |
|---------|------|------|
| Editable text | `class="mktEditable"` | `class="mktoText"` |
| Display name | `id` is used as display name | `mktoName` attribute provides display name |
| Modules/Containers | Not supported | `mktoModule` / `mktoContainer` |
| Variables | Not supported | `<meta class="mkto...">` in `<head>` |
| Drag-and-drop | Not supported | Supported via modules |
| Editor UI | Static canvas with editable zones | Modular panel with drag/drop/reorder |

### 1.3 Detection Checklist

> **If you see ANY of the following → it is a v2.0 template:**
> - [ ] `class="mktoContainer"` on any element
> - [ ] `class="mktoModule"` on any element
> - [ ] `class="mktoText"` on any element
> - [ ] `class="mktoImg"` on any element (in body, not `<meta>`)
> - [ ] `class="mktoSnippet"` on any element
> - [ ] `class="mktoVideo"` on any element
> - [ ] Any `<meta class="mktoString|mktoColor|mktoBoolean|mktoNumber|mktoList|mktoHTML|mktoImg">` in `<head>`
>
> **If you see ONLY `class="mktEditable"` and none of the above → it is a v1.0 template.**

### 1.4 Programmatic Detection (JavaScript)

```javascript
/**
 * Detects if a template string is Marketo v2.0
 * @param {string} html - The raw HTML of the template
 * @returns {object} - { version, features[], isHybrid }
 */
function detectMarketoVersion(html) {
    const v2Markers = {
        container:  /class\s*=\s*["'][^"']*\bmktoContainer\b[^"']*["']/,
        module:     /class\s*=\s*["'][^"']*\bmktoModule\b[^"']*["']/,
        text:       /class\s*=\s*["'][^"']*\bmktoText\b[^"']*["']/,
        img:        /class\s*=\s*["'][^"']*\bmktoImg\b[^"']*["']/,
        snippet:    /class\s*=\s*["'][^"']*\bmktoSnippet\b[^"']*["']/,
        video:      /class\s*=\s*["'][^"']*\bmktoVideo\b[^"']*["']/,
        variables:  /<meta\s+[^>]*class\s*=\s*["']\s*mkto(String|Boolean|Color|List|Number|HTML|Img)\s*["']/i
    };

    const v1Markers = {
        editable: /class\s*=\s*["'][^"']*\bmktEditable\b[^"']*["']/
    };

    let isV2 = false;
    let features = [];

    for (const [key, regex] of Object.entries(v2Markers)) {
        if (regex.test(html)) { isV2 = true; features.push(key); }
    }

    const hasV1 = v1Markers.editable.test(html);

    if (isV2) {
        return {
            version: '2.0',
            features,
            isHybrid: hasV1,
            warning: hasV1 ? 'Contains mktEditable — may cause legacy behavior within v2.0 parser' : null
        };
    } else if (hasV1) {
        return { version: '1.0', features: ['mktEditable'], isHybrid: false };
    } else {
        return { version: 'Unknown/Static', features: [], isHybrid: false };
    }
}
```

### 1.5 Hybrid Syntax Risk

**Rule:** Once a template contains any v2.0 marker, the v2.0 parser takes over. Legacy `mktEditable` elements will still render as basic Rich Text regions but lose v1.0-specific autonomy.

```html
<!-- ✅ CORRECT: Pure v2.0 -->
<div class="mktoText" id="bodyText" mktoName="Body Text">Content here</div>

<!-- ❌ INCORRECT: Mixing v1.0 and v2.0 in a template with mktoContainer -->
<div class="mktEditable" id="bodyText">Content here</div>
<!-- Result: May render as non-editable static HTML or basic RTE without mktoName label -->
```

> **⚠️ COMMUNITY-VERIFIED:** `mktEditable` inside a valid `mktoModule` does function as a Rich Text editor (confirmed in Marketo Nation). However, `mktoText` with explicit `mktoName` is strongly preferred for proper editor labeling.

---

## 2. Core v2.0 Class/Attribute Syntax

### 2.1 Element Type Reference

| Class | Purpose | Valid HTML Tags | Required Attributes | Optional Attributes |
|-------|---------|-----------------|--------------------|--------------------|
| `mktoText` | Rich Text Editor | `div` (preferred), `td`, `h1`–`h6`, `p` | `class`, `id`, `mktoName` | — |
| `mktoImg` (element) | Image Editor | `div` (preferred for linking), `img` | `class`, `id`, `mktoName` | `mktoImgClass`, `mktoImgSrc`, `mktoImgLink`, `mktoImgLinkTarget`, `mktoImgWidth`, `mktoImgHeight`, `mktoLockImgSize`, `mktoLockImgStyle` |
| `mktoSnippet` | Snippet Drop Zone | `div`, `td` | `class`, `id`, `mktoName` | `mktoDefaultSnippetId` |
| `mktoVideo` | Video Thumbnail | `div` | `class`, `id`, `mktoName` | `mktoImgClass` |
| `mktoModule` | Draggable Layout Block | `tr` (when container is `table`/`tbody`/`thead`/`tfoot`), `table` (when container is `td`) | `class`, `id`, `mktoName` | `mktoActive`, `mktoAddByDefault` |
| `mktoContainer` | Module Wrapper | `table`, `tbody`, `thead`, `tfoot`, `td` | `class`, `id` | — |

### 2.2 ID Format Rules

- **Allowed characters:** Letters (`a-z`, `A-Z`), numbers (`0-9`), dash (`-`), underscore (`_`)
- **No spaces allowed**
- **Must be unique** across the entire template (all elements, modules, variables, and containers)
- **When a module is duplicated** by the editor, Marketo appends a unique suffix (e.g., `heroModule_1a2b3c4d`)
- **CSS implication:** Never target modules by ID in CSS; use additional classes instead

```html
<!-- ✅ CORRECT IDs -->
<div class="mktoText" id="hero-text" mktoName="Hero Text">...</div>
<div class="mktoText" id="bodyContent_1" mktoName="Body Content">...</div>

<!-- ❌ INCORRECT IDs -->
<div class="mktoText" id="hero text" mktoName="Hero Text">...</div>     <!-- space -->
<div class="mktoText" id="hero.text" mktoName="Hero Text">...</div>     <!-- period -->
<div class="mktoText" id="heroText" mktoName="Hero A">...</div>
<div class="mktoText" id="heroText" mktoName="Hero B">...</div>         <!-- duplicate -->
```

### 2.3 mktoText — Rich Text Editor

**Recommended tag:** `<div>` inside a `<td>`, or directly on `<td>`.

**Why not `<span>`?** If a user inserts block-level elements (`<p>`, `<div>`, `<h2>`) via the Rich Text Editor into a `<span>`, it violates HTML5 content models and causes rendering issues especially in Outlook.

```html
<!-- ✅ PREFERRED: div inside td -->
<td align="center" style="padding: 20px;">
  <div class="mktoText" id="bodyContent" mktoName="Body Content">
    <h1 style="font-family: Arial, sans-serif;">Default Headline</h1>
    <p style="font-family: Arial, sans-serif;">Default body copy.</p>
  </div>
</td>

<!-- ✅ ACCEPTABLE: directly on td -->
<td class="mktoText" id="bodyContent" mktoName="Body Content"
    style="padding: 20px; font-family: Arial, sans-serif;">
  <p>Default body copy.</p>
</td>

<!-- ❌ AVOID: span (block-level content inserted by RTE breaks HTML5 model) -->
<span class="mktoText" id="bodyContent" mktoName="Body Content">Content</span>
```

**Attribute stripping:** When the email is compiled for sending, `class="mktoText"`, `mktoName`, and `id` are stripped from the final HTML. Only inner content and inline styles on the wrapper remain.

### 2.4 mktoImg — Image Editor

Two implementation patterns exist with significantly different capabilities:

#### Option A: Wrapper Div (Preferred)

Allows the user to add a hyperlink to the image via the editor.

```html
<!-- ✅ PREFERRED: Wrapper div allows linking -->
<div class="mktoImg" id="heroImage" mktoName="Hero Image"
     mktoImgLink="https://example.com"
     mktoImgLinkTarget="_blank"
     mktoLockImgSize="true">
  <a><img src="https://placehold.it/600x200" width="600"
          style="display: block; width: 100%; max-width: 600px;" border="0" alt="Hero"></a>
</div>
```

> **IMPORTANT:** When using Option A with default image styling, include the `<a></a>` wrapper around the `<img>` inside the div. If the user adds a link in the editor, Marketo wraps the `<img>` in an `<a>` tag. Including the empty `<a>` ensures your inline styles on the image won't be stripped when the link is added.

**Optional attributes for mktoImg (div):**

| Attribute | Type | Description | Default |
|-----------|------|-------------|---------|
| `mktoImgClass` | String | Added to the class of the inner `<img>` | — |
| `mktoImgSrc` | URL | Default image URL | Placeholder |
| `mktoImgLink` | URL | Default link URL wrapping the image | — |
| `mktoImgLinkTarget` | String | Link target (e.g., `_blank`) | — |
| `mktoImgWidth` | Number | Width of the enclosed `<img>` | — |
| `mktoImgHeight` | Number | Height of the enclosed `<img>` | — |
| `mktoLockImgSize` | Boolean | Lock image dimensions (`true`/`false`) | `true` |
| `mktoLockImgStyle` | Boolean | Lock `<img>` style property | `false` |

#### Option B: Direct Image Tag

User **cannot** add a hyperlink via the editor. Use for decorative images only.

```html
<!-- Acceptable for non-linkable images only -->
<img class="mktoImg" id="decorativeBanner" mktoName="Banner"
     src="https://placehold.it/600x100" width="600"
     style="display: block;" border="0" alt="Banner">
```

### 2.5 mktoSnippet — Snippet Drop Zone

```html
<div class="mktoSnippet" id="footerSnippet" mktoName="Footer Snippet"
     mktoDefaultSnippetId="1234"></div>
```

| Attribute | Required | Description |
|-----------|----------|-------------|
| `class="mktoSnippet"` | Yes | Declares snippet zone |
| `id` | Yes | Unique identifier |
| `mktoName` | Yes | Display name in editor |
| `mktoDefaultSnippetId` | No | Integer Asset ID of an approved snippet to pre-load |

**Constraints:**
- Snippets are rendered **after** variable processing. You cannot place `${variableID}` or `{{my.token}}` references inside a Snippet and expect them to resolve from the template's context.
- Snippets are effectively "black boxes" of pre-approved HTML.
- A `mktoSnippet` region **cannot** be converted to Rich Text. (The reverse — `mktoText` to Snippet — is allowed in the editor.)

### 2.6 mktoVideo — Video Thumbnail

```html
<div class="mktoVideo" id="productVideo" mktoName="Product Announcement Video"></div>
```

Allows insertion of a YouTube or Vimeo URL. Renders as a thumbnail image with a play button overlay. Since email clients don't support embedded video, clicking opens the video URL.

### 2.7 The Myth of mktoButton

**There is NO `mktoButton` class in Email Template 2.0.**

`mktoButton` exists **only** in Marketo Forms 2.0 (Landing Pages). To create editable buttons in email, use a table-based button structure with `mktoText` for the label and `mktoColor`/`mktoString` variables for styling:

```html
<!-- Email button using variables (inside a mktoModule) -->
<meta class="mktoString" id="ctaLink" mktoName="Button URL" default="https://example.com" mktoModuleScope="true">
<meta class="mktoColor" id="ctaBgColor" mktoName="Button Color" default="#0073e6" mktoModuleScope="true">
<meta class="mktoString" id="ctaTextColor" mktoName="Button Text Color" default="#ffffff" mktoModuleScope="true">

<!-- In the module body: -->
<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="border-collapse: separate;">
  <tr>
    <td align="center" bgcolor="${ctaBgColor}"
        style="border-radius: 4px; background-color: ${ctaBgColor};">
      <a href="${ctaLink}" target="_blank"
         style="display: inline-block; padding: 12px 24px;
                font-family: Arial, sans-serif; font-size: 16px;
                color: ${ctaTextColor}; text-decoration: none;">
        <span class="mktoText" id="ctaLabel" mktoName="Button Text">Learn More</span>
      </a>
    </td>
  </tr>
</table>
```

---

## 3. Modules and Containers

### 3.1 mktoContainer — The Root Drag Zone

**Rules:**
- **Exactly ONE per template.** Multiple containers → validation failure.
- **Valid elements:** `<table>`, `<tbody>`, `<thead>`, `<tfoot>`, `<td>`
- **STRICT content model:** A container can **ONLY** contain `mktoModule` elements as direct children. No stray HTML, no comments, no spacer divs, no `<br>` tags.
- **Required attribute:** `id` (unique)
- **Optional attribute:** `mktoName` (not shown in editor but good practice)

```html
<!-- ✅ CORRECT: table container with tr modules -->
<table class="mktoContainer" id="templateContainer" width="600"
       cellpadding="0" cellspacing="0" border="0">
  <tr class="mktoModule" id="headerModule" mktoName="Header">
    <td><!-- content --></td>
  </tr>
  <tr class="mktoModule" id="bodyModule" mktoName="Body">
    <td><!-- content --></td>
  </tr>
</table>

<!-- ✅ CORRECT: td container with table modules -->
<td class="mktoContainer" id="templateContainer">
  <table class="mktoModule" id="headerModule" mktoName="Header" width="100%">
    <tr><td><!-- content --></td></tr>
  </table>
  <table class="mktoModule" id="bodyModule" mktoName="Body" width="100%">
    <tr><td><!-- content --></td></tr>
  </table>
</td>

<!-- ❌ INCORRECT: Non-module content directly inside container -->
<table class="mktoContainer" id="templateContainer">
  <tr><td><!-- This static row triggers "Invalid Module" --></td></tr>
  <tr class="mktoModule" id="bodyModule" mktoName="Body">
    <td><!-- content --></td>
  </tr>
</table>

<!-- ❌ INCORRECT: HTML comment inside container -->
<table class="mktoContainer" id="templateContainer">
  <!-- Header section -->   <!-- THIS COMMENT CAN TRIGGER ERRORS -->
  <tr class="mktoModule" id="headerModule" mktoName="Header">
    <td><!-- content --></td>
  </tr>
</table>
```

### 3.2 Container-Module Pairing Rules

| Container Element | Module Element Must Be |
|-------------------|-----------------------|
| `<table>` | `<tr>` |
| `<tbody>` | `<tr>` |
| `<thead>` | `<tr>` |
| `<tfoot>` | `<tr>` |
| `<td>` | `<table>` |

```html
<!-- ❌ INCORRECT: table container with table modules -->
<table class="mktoContainer" id="container">
  <table class="mktoModule" id="mod1" mktoName="Module 1"><!-- WRONG --></table>
</table>

<!-- ❌ INCORRECT: td container with tr modules -->
<td class="mktoContainer" id="container">
  <tr class="mktoModule" id="mod1" mktoName="Module 1"><!-- WRONG --></tr>
</td>
```

### 3.3 mktoModule — Draggable Content Blocks

**Required attributes:**

| Attribute | Description |
|-----------|-------------|
| `class="mktoModule"` | Declares the element as a module |
| `id` | Unique identifier across the template |
| `mktoName` | Display name shown in the editor sidebar |

**Optional attributes:**

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `mktoActive` | Boolean | `true` | Whether the module appears in the module list for insertion |
| `mktoAddByDefault` | Boolean | `true` | Whether the module appears on the canvas when a new email is created (ignored if `mktoActive="false"`) |

### 3.4 Module Behavior Matrix

| `mktoActive` | `mktoAddByDefault` | Behavior |
|--------------|-------------------|----------|
| `true` | `true` | **Standard**: On canvas by default, available in module list for duplication/re-adding |
| `true` | `false` | **Optional**: NOT on canvas by default, but available in module list to drag in |
| `false` | `true` | **Ghost/Locked**: On canvas by default, but NOT in module list. If user deletes it, it cannot be re-added. Useful for mandatory headers/footers. |
| `false` | `false` | **Hidden/Deprecated**: Not on canvas, not in module list. Completely inaccessible. Useful for deprecating modules without removing code. |

```html
<!-- Standard module: on canvas + in list -->
<tr class="mktoModule" id="heroModule" mktoName="Hero Section"
    mktoActive="true" mktoAddByDefault="true">
  <td><!-- content --></td>
</tr>

<!-- Optional module: user must drag it in -->
<tr class="mktoModule" id="testimonialModule" mktoName="Testimonial"
    mktoActive="true" mktoAddByDefault="false">
  <td><!-- content --></td>
</tr>

<!-- Locked footer: always present, cannot be removed and re-added -->
<tr class="mktoModule" id="footerModule" mktoName="Footer"
    mktoActive="false" mktoAddByDefault="true">
  <td><!-- content --></td>
</tr>
```

### 3.5 Nesting and Stacking Rules

| Rule | Details |
|------|---------|
| **No module nesting** | A `mktoModule` **cannot** contain another `mktoModule`. Hierarchy is strictly one level deep. |
| **No horizontal stacking** | You cannot place two modules side-by-side (e.g., two `<td>` modules in one `<tr>`). The container stack is **vertical only**. |
| **No container nesting** | Only one `mktoContainer` per template. Cannot nest containers. |
| **Columns within modules** | To achieve column layouts, build columns **inside** a single module using nested tables. |

```html
<!-- ❌ INCORRECT: Nested modules -->
<tr class="mktoModule" id="outerModule" mktoName="Outer">
  <td>
    <table>
      <tr class="mktoModule" id="innerModule" mktoName="Inner">
        <td><!-- INVALID --></td>
      </tr>
    </table>
  </td>
</tr>

<!-- ❌ INCORRECT: Side-by-side modules -->
<tr>
  <td class="mktoModule" id="leftModule" mktoName="Left"><!-- INVALID --></td>
  <td class="mktoModule" id="rightModule" mktoName="Right"><!-- INVALID --></td>
</tr>

<!-- ✅ CORRECT: Columns INSIDE a single module -->
<tr class="mktoModule" id="twoColModule" mktoName="Two Columns">
  <td>
    <table width="100%">
      <tr>
        <td width="50%" valign="top"><!-- Left column content --></td>
        <td width="50%" valign="top"><!-- Right column content --></td>
      </tr>
    </table>
  </td>
</tr>
```

---

## 4. `<meta>` Variable Declarations

Variables are declared as `<meta>` tags in the `<head>` section. They provide editor UI controls (color pickers, text inputs, toggles, dropdowns) and are referenced in the body HTML using `${variableID}` syntax.

### 4.1 Complete Variable Type Reference

| Variable Class | Editor UI | Required Attrs | Optional Attrs |
|---------------|-----------|---------------|----------------|
| `mktoString` | Text input | `id`, `mktoName` | `default`, `allowHTML`, `mktoModuleScope` |
| `mktoColor` | Color picker | `id`, `mktoName` | `default` (6-digit hex), `mktoModuleScope` |
| `mktoBoolean` | Toggle switch | `id`, `mktoName` | `default`, `true_value`, `false_value`, `true_value_name`, `false_value_name`, `mktoModuleScope` |
| `mktoNumber` | Numeric spinner | `id`, `mktoName`, `default` | `min`, `max`, `units`, `step`, `mktoModuleScope` |
| `mktoList` | Dropdown select | `id`, `mktoName`, `values` | `default`, `mktoModuleScope` |
| `mktoHTML` | HTML code input | `id`, `mktoName` | `default` (HTML-encoded), `mktoModuleScope` |
| `mktoImg` (meta) | Image picker (URL only) | `id`, `mktoName` | `default` (image URL), `mktoModuleScope` |

> **⚠️ NOTE on `mktoImg` as variable vs element:** When `mktoImg` appears on a `<meta>` tag in the `<head>`, it is an **Image Variable** that returns a URL string. When it appears as a `class` on a `<div>` or `<img>` in the body, it is an **Image Element** that inserts an `<img>` DOM element. These are different things.

### 4.2 Syntax for Each Variable Type

#### mktoString

```html
<!-- Declaration in <head> -->
<meta class="mktoString" id="preheaderText" mktoName="Preheader Text"
      default="View this email in your browser" allowHTML="false">

<!-- Usage in body -->
<span style="display: none;">${preheaderText}</span>
```

| Attribute | Required | Type | Default | Notes |
|-----------|----------|------|---------|-------|
| `id` | Yes | String | — | Must match `${id}` reference |
| `mktoName` | Yes | String | — | Editor display label |
| `default` | No | String | Blank | Default text value |
| `allowHTML` | No | Boolean | `false` | If `true`, value is NOT HTML-escaped. **Use with caution.** |
| `mktoModuleScope` | No | Boolean | `false` | `true` = local to each module instance |

#### mktoColor

```html
<!-- Declaration -->
<meta class="mktoColor" id="headerBgColor" mktoName="Header Background"
      default="#1a2b3c" mktoModuleScope="false">

<!-- Usage -->
<td style="background-color: ${headerBgColor};">
```

> **Constraint:** Default must be a **6-digit hex color code** including the `#`. RGB, RGBA, HSL, and color names are **not accepted** as defaults.

```html
<!-- ✅ CORRECT -->
<meta class="mktoColor" id="bgColor" mktoName="BG" default="#ff6600">

<!-- ❌ INCORRECT -->
<meta class="mktoColor" id="bgColor" mktoName="BG" default="rgb(255,102,0)">
<meta class="mktoColor" id="bgColor" mktoName="BG" default="orange">
<meta class="mktoColor" id="bgColor" mktoName="BG" default="#f60">  <!-- 3-digit shorthand -->
```

#### mktoBoolean

```html
<!-- Declaration -->
<meta class="mktoBoolean" id="showHeroSection" mktoName="Show Hero?"
      default="true"
      true_value="block" false_value="none"
      true_value_name="Show" false_value_name="Hide"
      mktoModuleScope="true">

<!-- Usage: Toggle visibility -->
<div style="display: ${showHeroSection};">
  <!-- Hero content -->
</div>
```

| Attribute | Required | Default | Notes |
|-----------|----------|---------|-------|
| `default` | No | `false` | Initial toggle state |
| `true_value` | No | `true` | Value inserted when ON |
| `false_value` | No | `false` | Value inserted when OFF |
| `true_value_name` | No | `true` | Label shown in UI for ON |
| `false_value_name` | No | `false` | Label shown in UI for OFF |

#### mktoNumber

```html
<!-- Declaration -->
<meta class="mktoNumber" id="spacerHeight" mktoName="Spacer Height"
      default="20" min="0" max="100" units="px" step="5"
      mktoModuleScope="true">

<!-- Usage -->
<td style="height: ${spacerHeight};"></td>
```

| Attribute | Required | Default | Notes |
|-----------|----------|---------|-------|
| `default` | **Yes** | — | Default numeric value |
| `min` | No | — | Minimum allowed value |
| `max` | No | — | Maximum allowed value |
| `units` | No | — | Appended to value in editor UI AND output (e.g., `px`, `%`) |
| `step` | No | `1` | Increment/decrement step |

#### mktoList

```html
<!-- Declaration -->
<meta class="mktoList" id="fontFamily" mktoName="Font"
      values="Arial,Verdana,Georgia,Times New Roman"
      default="Arial" mktoModuleScope="false">

<!-- Usage -->
<td style="font-family: ${fontFamily}, sans-serif;">
```

| Attribute | Required | Default | Notes |
|-----------|----------|---------|-------|
| `values` | **Yes** | — | Comma-separated list. Must have at least one value. |
| `default` | No | First value in `values` | Must be one of the `values` |

#### mktoHTML

```html
<!-- Declaration -->
<meta class="mktoHTML" id="trackingPixel" mktoName="Custom Tracking Code"
      default="&lt;!-- tracking code here --&gt;">

<!-- Usage -->
${trackingPixel}
```

The user can input raw HTML via the editor. The `default` value must be **HTML-encoded** in the `<meta>` tag.

#### mktoImg (as variable)

```html
<!-- Declaration -->
<meta class="mktoImg" id="heroBgImage" mktoName="Hero Background Image"
      default="https://www.example.com/images/hero.jpg" mktoModuleScope="true">

<!-- Usage: As CSS background image -->
<td style="background-image: url('${heroBgImage}');">
```

This returns only the **URL string**, unlike the `mktoImg` element class which inserts an `<img>` DOM element.

### 4.3 Variable Scoping: `mktoModuleScope`

| Setting | Behavior |
|---------|----------|
| `mktoModuleScope="false"` (or omitted) | **Global**: Value is shared across the entire email. Changing it in one place updates everywhere. |
| `mktoModuleScope="true"` | **Local**: Each module instance gets its own independent copy of the variable. |

**When to use Global:**
- Brand colors that must be consistent across all modules
- Footer links, legal text
- Preheader text, company name

**When to use Local:**
- Button URLs (each CTA may link somewhere different)
- Section background colors (each section may vary)
- Show/hide toggles for individual sections
- Per-module image sources

```html
<!-- Global: Same color everywhere -->
<meta class="mktoColor" id="brandColor" mktoName="Brand Color" default="#0073e6">

<!-- Local: Each module instance gets its own copy -->
<meta class="mktoColor" id="sectionBg" mktoName="Section Background" default="#ffffff" mktoModuleScope="true">
```

### 4.4 Variable Reference Syntax

Variables are referenced using `${variableID}` anywhere in the body HTML — in attributes, in inline styles, in text content.

```html
<!-- In style attributes -->
<td style="background-color: ${bgColor}; padding: ${contentPadding};">

<!-- In href attributes -->
<a href="${ctaUrl}" style="color: ${linkColor};">

<!-- In text content -->
<p>${greeting}</p>

<!-- In CSS (global <style> block — only for global variables) -->
<style>
  .header { background-color: ${headerBg} !important; }
</style>
```

> **⚠️ CRITICAL SCOPING RULE:** If a variable is **local** (`mktoModuleScope="true"`), do NOT reference it in the global `<style>` block in the `<head>`. The `<head>` is outside any module's scope, so Marketo cannot resolve which module instance's value to use. **Local variables must only be referenced in inline `style` attributes within their module.**

```html
<!-- ✅ CORRECT: Local variable in inline style -->
<td style="background-color: ${sectionBg};"><!-- inside a module --></td>

<!-- ❌ INCORRECT: Local variable in global <style> block -->
<style>
  .section { background-color: ${sectionBg}; }  /* Cannot resolve — which module? */
</style>
```

---

## 5. Mobile Responsive Patterns for v2.0

### 5.1 Approach Overview

The responsive approach in v2.0 is functionally the same as v1.0 — table-based layouts with CSS media queries and `!important` overrides — but with one key architectural constraint: **responsive columns must be built inside a single module** because modules stack vertically only.

### 5.2 The `!important` Requirement

Marketo frequently inlines styles or adds specificity. Almost all media query rules **require `!important`** to override desktop inline styles.

```css
/* ✅ CORRECT: !important on every mobile override */
@media only screen and (max-width: 480px) {
  .mobile-full { width: 100% !important; max-width: 100% !important; }
  .mobile-stack { display: block !important; width: 100% !important; }
  .mobile-pad { padding: 15px !important; }
  .mobile-hide { display: none !important; }
  .mobile-center { text-align: center !important; }
}

/* ❌ INCORRECT: Missing !important (will be overridden by inline styles) */
@media only screen and (max-width: 480px) {
  .mobile-full { width: 100%; }
}
```

### 5.3 CSS Targeting: Classes, Not IDs

When a module is duplicated, Marketo appends a unique suffix to the module's `id` but does **not** rename classes. Therefore:

```css
/* ✅ CORRECT: Target by class (works on all module instances) */
.hero-section { background-color: #f0f0f0; }

/* ❌ INCORRECT: Target by module ID (breaks on duplicated modules) */
#heroModule { background-color: #f0f0f0; }
/* Duplicated module becomes #heroModule_a1b2c3d4 — this CSS won't match */
```

**Best practice:** Add a secondary CSS class alongside `mktoModule` for styling:

```html
<tr class="mktoModule hero-section" id="heroModule" mktoName="Hero Section">
```

### 5.4 Responsive Two-Column Pattern (Inside a Module)

```html
<tr class="mktoModule" id="twoColModule" mktoName="Two Columns">
  <td align="center" style="padding: 20px;">
    <table width="600" cellpadding="0" cellspacing="0" border="0" role="presentation"
           class="mobile-full" style="width: 600px;">
      <tr>
        <!-- Left Column -->
        <td width="290" valign="top" class="mobile-stack"
            style="width: 290px; padding-right: 10px;">
          <div class="mktoText" id="leftColText" mktoName="Left Column">
            <p>Left column content</p>
          </div>
        </td>
        <!-- Right Column -->
        <td width="290" valign="top" class="mobile-stack"
            style="width: 290px; padding-left: 10px;">
          <div class="mktoText" id="rightColText" mktoName="Right Column">
            <p>Right column content</p>
          </div>
        </td>
      </tr>
    </table>
  </td>
</tr>
```

With this CSS in the `<head>`:

```css
@media only screen and (max-width: 480px) {
  .mobile-full { width: 100% !important; }
  .mobile-stack {
    display: block !important;
    width: 100% !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
  }
}
```

### 5.5 Ghost Table Pattern for Outlook

Since Outlook ignores `display: block` stacking, use conditional comments for Outlook-specific fixed-width tables:

```html
<!--[if mso]>
<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td width="290" valign="top">
<![endif]-->
      <!-- Left column (fluid) -->
<!--[if mso]>
    </td>
    <td width="290" valign="top">
<![endif]-->
      <!-- Right column (fluid) -->
<!--[if mso]>
    </td>
  </tr>
</table>
<![endif]-->
```

---

## 6. CSS and Inlining in v2.0

### 6.1 Inlining Behavior

Marketo provides an "Inline CSS" tool under Email Template Actions. Behavior:

- It parses the `<style>` block and applies matching rules as inline `style` attributes.
- **It does NOT inline media queries** — these remain in the `<style>` block (which is correct).
- **Best practice for v2.0:** Pre-inline your desktop styles directly in the HTML. Use the `<style>` block **only** for media queries, pseudo-classes (`:hover`), and any styles that require `!important` for mobile.

### 6.2 Variables in CSS

Marketo resolves `${variableID}` substitutions **before** the email is rendered. This means variables work inside inline `style` attributes and in `<style>` blocks (for global variables only).

```html
<!-- ✅ CORRECT: Global variable in <style> block -->
<style>
  .header { background-color: ${brandColor} !important; }
</style>

<!-- ✅ CORRECT: Any variable in inline style -->
<td style="background-color: ${sectionBg}; color: ${textColor};">

<!-- ❌ INCORRECT: Local variable in <style> block (cannot resolve scope) -->
<style>
  .cta-btn { background-color: ${ctaBgColor} !important; }
  /* If ctaBgColor is mktoModuleScope="true", this fails */
</style>
```

### 6.3 Media Query Handling

Same `!important` requirement as v1.0. Media queries belong in `<style>` in the `<head>`, never inline.

```html
<head>
  <style type="text/css">
    /* ONLY media queries and pseudo-classes in <style> block */
    @media only screen and (max-width: 480px) {
      .mobile-full { width: 100% !important; max-width: 100% !important; }
      .mobile-stack { display: block !important; width: 100% !important; }
    }
    /* Hover states */
    a.cta-btn:hover { background-color: #005bb5 !important; }
  </style>
</head>
```

---

## 7. Velocity Tokens in v2.0

### 7.1 Processing Order

Understanding the processing order is essential:

1. **Pass 1 — Template Variables:** Marketo resolves all `${variableID}` references from `<meta>` declarations.
2. **Pass 2 — Velocity/Tokens:** Marketo resolves all `{{my.token}}`, `{{lead.Field}}`, `{{system.token}}` references.

### 7.2 Standard Token Syntax (Same as v1.0)

| Token Type | Syntax | Example |
|-----------|--------|---------|
| Lead/Person field | `{{lead.Field Name}}` | `{{lead.First Name}}` |
| Company field | `{{company.Field Name}}` | `{{company.Company Name}}` |
| System token | `{{system.tokenName}}` | `{{system.unsubscribeLink}}` |
| My Token (program) | `{{my.Token Name}}` | `{{my.CTA URL}}` |

All token types work identically in v2.0 as in v1.0. They resolve at send time.

### 7.3 Variables + Tokens Interaction

You **can** use a Velocity token as the default value of a meta variable:

```html
<meta class="mktoString" id="greeting" mktoName="Greeting"
      default="Hello {{lead.First Name}}">
```

The editor displays `Hello {{lead.First Name}}` as the editable string. At send time, Marketo resolves the token within the string.

You generally **cannot** use `${variableID}` inside a Velocity script block, because template variable resolution (Pass 1) occurs before Velocity processing (Pass 2). The resolved value would be a literal string by the time Velocity runs, which may or may not be useful depending on context.

### 7.4 System Tokens for Compliance

These must be present in every marketing email:

```html
<!-- Unsubscribe link (REQUIRED for marketing emails) -->
<a href="{{system.unsubscribeLink}}" style="color: #999999;">Unsubscribe</a>

<!-- View as web page (optional but recommended) -->
<a href="{{system.viewAsWebpageLink}}" style="color: #999999;">View in browser</a>

<!-- Forward to a friend -->
<a href="{{system.forwardToFriendLink}}">Forward</a>
```

> **Placement rule:** System tokens must be placed inside an editable region (`mktoText`) or directly in a module's static HTML. They render correctly in both contexts. Placing them inside a `mktoSnippet` will **not** work — snippets don't process parent template tokens.

### 7.5 Escape Rules

| Character | Conflict | Solution |
|-----------|----------|----------|
| `#` | Velocity directive prefix | Generally safe in standard CSS `#id` selectors because Velocity only processes explicit directives. Use `$esc.h` only if template HTML passes through Velocity engine directly. |
| `$` | Velocity variable prefix | `${variableID}` is resolved in Pass 1 (template variables), not Velocity. Actual Velocity `$` variables only matter in Velocity script tokens. |

---

## 8. Validation Rules

### 8.1 Template Validity Requirements

| Requirement | Status | Notes |
|-------------|--------|-------|
| Valid HTML structure | Required | Unclosed tags are the #1 cause of "Invalid Module" errors |
| Exactly one `mktoContainer` | Required (if using modules) | Zero containers = no module functionality. Two+ = validation failure. |
| Modules as direct children of container only | Required | Any non-module element directly inside container = "Invalid Module" |
| Matching container-module element types | Required | See pairing rules in §3.2 |
| Unique IDs on all elements | Required | Duplicates cause "Duplicate Element Id" error |
| No nested modules | Required | Module inside module = "Invalid Module" |
| At least one editable element | Recommended | Template is technically valid without one but provides no editing capability |

> **⚠️ DOCUMENTATION GAP:** Official docs state containers can "only contain Modules" but do not clarify whether HTML comments inside the container trigger errors. Community reports confirm that stray comments, `<br>` tags, and whitespace text nodes CAN trigger "Invalid Module" errors in some parser versions.

### 8.2 Common Validation Errors

| Error Message | Cause | Fix |
|---------------|-------|-----|
| `Invalid Module: #containerId > element:nth-child(N)` | Non-module element as direct child of container | Remove stray HTML; ensure every direct child has `class="mktoModule"` |
| `Invalid Module: #moduleId` | Module not properly nested, wrong element type for container, or unclosed tags | Check container-module pairing; validate HTML tag closure |
| `Duplicate Element Id` | Two or more elements share the same `id` | Make all IDs unique |
| `Unused Variable` | `<meta>` variable declared but not referenced via `${id}` | Remove unused `<meta>` tag (warning only; not a blocking error) |
| `Element With No Name` | `mktoModule` or other mkto element missing `mktoName` | Add `mktoName` attribute |
| `Invalid Field Value` | Variable default doesn't match expected format (e.g., `mktoColor` with RGB instead of hex) | Use correct format for variable type |

### 8.3 Debugging Steps for "Invalid Module"

1. **Validate HTML:** Use an HTML linter or [HTML Tidy Online](https://htmltidy.net/) to check for unclosed tags.
2. **Check container content:** Ensure every direct child of `mktoContainer` has `class="mktoModule"` and nothing else exists at that level.
3. **Check element pairing:** If container is `<table>`, modules must be `<tr>`. If container is `<td>`, modules must be `<table>`.
4. **Isolate modules:** Remove modules one by one to identify the offending module.
5. **Check for duplicate IDs:** Search for all `id=` values and confirm uniqueness.
6. **Use Marketo's validator:** Template Actions → Validate HTML (shows error list).

### 8.4 Edge Cases

| Scenario | Behavior |
|----------|----------|
| Empty module (mktoModule with no content) | Valid but renders as empty space. Not recommended. |
| Module with no editable elements | Valid. Module appears in sidebar but has no editable fields when selected. |
| Container with no modules | **Technically valid** but template has no modular functionality. |
| Template with editable elements but no container or modules | Valid v2.0 "flat" template — functions like an enhanced v1.0 template with v2.0 editor features. |
| Multiple `mktoText` on the same element | Only the first class match is processed. Avoid. |

---

## 9. Complete Template Archetypes

### 9.1 Single-Column Newsletter Template

```html
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${emailSubject}</title>

  <!-- ========== GLOBAL VARIABLES ========== -->
  <meta class="mktoString" id="emailSubject" mktoName="Email Subject (title tag)" default="Newsletter">
  <meta class="mktoString" id="preheaderText" mktoName="Preheader Text" default="Your monthly update is here.">
  <meta class="mktoColor" id="bodyBgColor" mktoName="Page Background Color" default="#f4f4f4">
  <meta class="mktoColor" id="contentBgColor" mktoName="Content Background Color" default="#ffffff">
  <meta class="mktoColor" id="brandColor" mktoName="Brand Color" default="#0073e6">
  <meta class="mktoString" id="fontStack" mktoName="Font Stack" default="Arial, Helvetica, sans-serif" allowHTML="true">

  <!-- ========== LOCAL (MODULE-SCOPED) VARIABLES ========== -->
  <meta class="mktoColor" id="sectionBgColor" mktoName="Section Background" default="#ffffff" mktoModuleScope="true">
  <meta class="mktoString" id="ctaLink" mktoName="Button URL" default="https://example.com" mktoModuleScope="true">
  <meta class="mktoColor" id="ctaBgColor" mktoName="Button Background" default="#0073e6" mktoModuleScope="true">
  <meta class="mktoColor" id="ctaTextColor" mktoName="Button Text Color" default="#ffffff" mktoModuleScope="true">
  <meta class="mktoBoolean" id="showSection" mktoName="Show This Section?" default="true"
        true_value="block" false_value="none" true_value_name="Show" false_value_name="Hide"
        mktoModuleScope="true">
  <meta class="mktoNumber" id="sectionPadding" mktoName="Section Padding" default="30"
        min="0" max="80" units="px" step="5" mktoModuleScope="true">

  <style type="text/css">
    /* Reset */
    body, table, td, a { -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }
    table, td { mso-table-lspace: 0pt; mso-table-rspace: 0pt; }
    img { -ms-interpolation-mode: bicubic; border: 0; outline: none; text-decoration: none; }

    /* Mobile */
    @media only screen and (max-width: 480px) {
      .mobile-full { width: 100% !important; max-width: 100% !important; }
      .mobile-stack { display: block !important; width: 100% !important; }
      .mobile-pad { padding: 20px !important; }
      .mobile-center { text-align: center !important; }
      .mobile-hide { display: none !important; max-height: 0 !important; overflow: hidden !important; }
      .mobile-img { width: 100% !important; height: auto !important; }
    }
  </style>

  <!--[if mso]>
  <style type="text/css">
    body, table, td { font-family: Arial, Helvetica, sans-serif !important; }
  </style>
  <![endif]-->
</head>
<body style="margin: 0; padding: 0; background-color: ${bodyBgColor}; -webkit-font-smoothing: antialiased;">

  <!-- Preheader (hidden preview text) -->
  <div style="display: none; max-height: 0; overflow: hidden; font-size: 1px; line-height: 1px; color: ${bodyBgColor};">
    ${preheaderText}
  </div>

  <!-- Outer Wrapper -->
  <table width="100%" cellpadding="0" cellspacing="0" border="0" role="presentation"
         style="background-color: ${bodyBgColor};">
    <tr>
      <td align="center" style="padding: 20px 10px;">

        <!-- ========== CONTAINER ========== -->
        <table class="mktoContainer" id="templateContainer" width="600"
               cellpadding="0" cellspacing="0" border="0" role="presentation"
               class="mobile-full" style="width: 600px; background-color: ${contentBgColor};">

          <!-- ===== PREHEADER MODULE ===== -->
          <tr class="mktoModule" id="preheaderModule" mktoName="Preheader Bar"
              mktoActive="true" mktoAddByDefault="true">
            <td align="center" style="padding: 10px 20px; font-family: ${fontStack}; font-size: 12px; color: #888888;">
              <div class="mktoText" id="preheaderContent" mktoName="Preheader Content">
                <a href="{{system.viewAsWebpageLink}}" style="color: #888888; text-decoration: underline;">View in browser</a>
              </div>
            </td>
          </tr>

          <!-- ===== HEADER / LOGO MODULE ===== -->
          <tr class="mktoModule" id="headerModule" mktoName="Header / Logo"
              mktoActive="false" mktoAddByDefault="true">
            <td align="center" style="padding: 30px 20px; background-color: ${sectionBgColor};">
              <div class="mktoImg" id="logoImage" mktoName="Logo"
                   mktoImgWidth="200" mktoLockImgSize="false">
                <img src="https://placehold.it/200x60/0073e6/ffffff?text=LOGO" width="200"
                     style="display: block; max-width: 200px;" alt="Company Logo" />
              </div>
            </td>
          </tr>

          <!-- ===== HERO IMAGE MODULE ===== -->
          <tr class="mktoModule" id="heroModule" mktoName="Hero Image"
              mktoActive="true" mktoAddByDefault="true">
            <td align="center" style="display: ${showSection};">
              <div class="mktoImg" id="heroImage" mktoName="Hero Image"
                   mktoImgLink="${ctaLink}" mktoLockImgSize="true">
                <a><img src="https://placehold.it/600x300" width="600"
                     style="display: block; width: 100%; max-width: 600px; height: auto;"
                     class="mobile-img" alt="Hero Image" border="0" /></a>
              </div>
            </td>
          </tr>

          <!-- ===== BODY TEXT MODULE ===== -->
          <tr class="mktoModule" id="bodyTextModule" mktoName="Body Text Block"
              mktoActive="true" mktoAddByDefault="true">
            <td align="center"
                style="display: ${showSection}; padding: ${sectionPadding}; background-color: ${sectionBgColor};"
                class="mobile-pad">
              <div class="mktoText" id="bodyTextContent" mktoName="Body Text">
                <h1 style="margin: 0 0 15px 0; font-family: ${fontStack}; font-size: 28px; line-height: 34px; color: #222222;">
                  Your Headline Goes Here
                </h1>
                <p style="margin: 0 0 20px 0; font-family: ${fontStack}; font-size: 16px; line-height: 24px; color: #555555;">
                  Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam.
                </p>
              </div>
            </td>
          </tr>

          <!-- ===== CTA BUTTON MODULE ===== -->
          <tr class="mktoModule" id="ctaButtonModule" mktoName="CTA Button"
              mktoActive="true" mktoAddByDefault="true">
            <td align="center"
                style="display: ${showSection}; padding: 0 30px 30px 30px; background-color: ${sectionBgColor};">
              <table border="0" cellpadding="0" cellspacing="0" role="presentation"
                     style="border-collapse: separate;">
                <tr>
                  <td align="center" bgcolor="${ctaBgColor}"
                      style="border-radius: 4px; background-color: ${ctaBgColor};">
                    <!--[if mso]>
                    <v:roundrect xmlns:v="urn:schemas-microsoft-com:vml"
                                 xmlns:w="urn:schemas-microsoft-com:office:word"
                                 href="${ctaLink}" style="height:48px;v-text-anchor:middle;width:200px;"
                                 arcsize="8%" fillcolor="${ctaBgColor}" stroke="false">
                      <w:anchorlock/>
                      <center style="color:${ctaTextColor};font-family:Arial,sans-serif;font-size:16px;font-weight:bold;">
                    <![endif]-->
                    <a href="${ctaLink}" target="_blank"
                       style="display: inline-block; padding: 14px 30px;
                              font-family: ${fontStack}; font-size: 16px; font-weight: bold;
                              color: ${ctaTextColor}; text-decoration: none; border-radius: 4px;
                              -webkit-text-size-adjust: none; mso-hide: all;">
                      <span class="mktoText" id="ctaButtonText" mktoName="Button Label">Get Started</span>
                    </a>
                    <!--[if mso]>
                      </center>
                    </v:roundrect>
                    <![endif]-->
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- ===== DIVIDER MODULE ===== -->
          <tr class="mktoModule" id="dividerModule" mktoName="Divider Line"
              mktoActive="true" mktoAddByDefault="false">
            <td align="center" style="padding: 0 30px;">
              <table width="100%" cellpadding="0" cellspacing="0" border="0" role="presentation">
                <tr>
                  <td style="border-top: 1px solid #eeeeee; font-size: 1px; line-height: 1px;">&nbsp;</td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- ===== FOOTER MODULE ===== -->
          <tr class="mktoModule" id="footerModule" mktoName="Footer"
              mktoActive="false" mktoAddByDefault="true">
            <td align="center" style="padding: 30px 20px; background-color: ${sectionBgColor};"
                class="mobile-pad">
              <div class="mktoText" id="footerContent" mktoName="Footer Text">
                <p style="margin: 0 0 10px 0; font-family: ${fontStack}; font-size: 12px; line-height: 18px; color: #999999;">
                  &copy; 2025 Company Name, 123 Main Street, City, State 00000
                </p>
                <p style="margin: 0; font-family: ${fontStack}; font-size: 12px; line-height: 18px; color: #999999;">
                  <a href="{{system.unsubscribeLink}}" style="color: #999999; text-decoration: underline;">Unsubscribe</a>
                  &nbsp;|&nbsp;
                  <a href="#" style="color: #999999; text-decoration: underline;">Privacy Policy</a>
                </p>
              </div>
            </td>
          </tr>

        </table>
        <!-- END CONTAINER -->

      </td>
    </tr>
  </table>

</body>
</html>
```

### 9.2 Two-Column Responsive Module

This module can be inserted inside the container above for a two-column layout that stacks on mobile:

```html
<!-- ===== TWO-COLUMN MODULE ===== -->
<tr class="mktoModule" id="twoColumnModule" mktoName="Two Column Layout"
    mktoActive="true" mktoAddByDefault="false">
  <td align="center"
      style="display: ${showSection}; padding: ${sectionPadding}; background-color: ${sectionBgColor};"
      class="mobile-pad">

    <!--[if mso]>
    <table role="presentation" width="540" cellpadding="0" cellspacing="0" border="0">
      <tr>
        <td width="260" valign="top">
    <![endif]-->

    <!-- LEFT COLUMN -->
    <div style="display: inline-block; vertical-align: top; width: 260px; max-width: 260px;"
         class="mobile-stack">
      <table width="100%" cellpadding="0" cellspacing="0" border="0" role="presentation">
        <tr>
          <td style="padding: 0 10px 20px 0;" class="mobile-pad">
            <div class="mktoImg" id="leftColImage" mktoName="Left Column Image"
                 mktoLockImgSize="false">
              <img src="https://placehold.it/260x180" width="260"
                   style="display: block; width: 100%; height: auto;" alt="" border="0" />
            </div>
            <div class="mktoText" id="leftColContent" mktoName="Left Column Text">
              <h3 style="margin: 15px 0 8px 0; font-family: ${fontStack}; font-size: 18px; color: #222222;">
                Left Column Title
              </h3>
              <p style="margin: 0; font-family: ${fontStack}; font-size: 14px; line-height: 20px; color: #555555;">
                Description text for the left column content area.
              </p>
            </div>
          </td>
        </tr>
      </table>
    </div>

    <!--[if mso]>
        </td>
        <td width="260" valign="top">
    <![endif]-->

    <!-- RIGHT COLUMN -->
    <div style="display: inline-block; vertical-align: top; width: 260px; max-width: 260px;"
         class="mobile-stack">
      <table width="100%" cellpadding="0" cellspacing="0" border="0" role="presentation">
        <tr>
          <td style="padding: 0 0 20px 10px;" class="mobile-pad">
            <div class="mktoImg" id="rightColImage" mktoName="Right Column Image"
                 mktoLockImgSize="false">
              <img src="https://placehold.it/260x180" width="260"
                   style="display: block; width: 100%; height: auto;" alt="" border="0" />
            </div>
            <div class="mktoText" id="rightColContent" mktoName="Right Column Text">
              <h3 style="margin: 15px 0 8px 0; font-family: ${fontStack}; font-size: 18px; color: #222222;">
                Right Column Title
              </h3>
              <p style="margin: 0; font-family: ${fontStack}; font-size: 14px; line-height: 20px; color: #555555;">
                Description text for the right column content area.
              </p>
            </div>
          </td>
        </tr>
      </table>
    </div>

    <!--[if mso]>
        </td>
      </tr>
    </table>
    <![endif]-->

  </td>
</tr>
```

---

## 10. Link Best Practices in v2.0

### 10.1 Tracking Behavior

Marketo automatically wraps all links in a tracking redirect (e.g., `https://click.marketo.com/...`). This applies to:

- Static `<a href="...">` links
- Links inside `mktoText` regions (user-added via RTE)
- Links generated by `mktoImgLink` on `mktoImg` elements
- `${variableID}` URLs that resolve to full URLs

### 10.2 Link Rules

| Rule | Details |
|------|---------|
| **Always use absolute URLs** | `https://example.com/page` not `/page` |
| **Include protocol in variable values** | If `ctaLink` variable is used for `href`, the value must include `https://`. Do NOT build `href="https://${ctaLink}"` — include the protocol in the variable default/value. |
| **Inline styles on links** | Always inline-style `<a>` tags. Some clients strip `<style>` blocks. |
| **System tokens in links** | `{{system.unsubscribeLink}}` renders the full URL including protocol — use it directly as `href` value. |

```html
<!-- ✅ CORRECT: Full URL in variable -->
<meta class="mktoString" id="ctaUrl" mktoName="Button URL" default="https://example.com/offer">
<a href="${ctaUrl}">Click Here</a>

<!-- ❌ INCORRECT: Protocol hardcoded separately -->
<meta class="mktoString" id="ctaUrl" mktoName="Button URL" default="example.com/offer">
<a href="https://${ctaUrl}">Click Here</a>
<!-- Breaks if user enters "https://example.com" — becomes "https://https://example.com" -->
```

### 10.3 mktoImgLink Behavior

When using the `mktoImg` wrapper div pattern:

- If the user provides a link → Marketo wraps the `<img>` in a tracked `<a>` tag
- If the user leaves the link field empty → No `<a>` tag is generated
- Links generated by `mktoImgLink` are automatically tracked

---

## 11. Forbidden Patterns (Quick Reference)

| Pattern | Why It's Forbidden | Fix |
|---------|-------------------|-----|
| Multiple `mktoContainer` elements | Parser requires exactly one | Use one container wrapping all modules |
| Non-module HTML inside `mktoContainer` | Container can only contain modules | Move all non-module HTML into modules or outside the container |
| Nested `mktoModule` elements | One-level hierarchy only | Flatten structure; build complex layouts inside a single module |
| Duplicate `id` values | Parser crash / random suffixes | Make all IDs unique |
| `mktotext` (wrong case) | Class names are case-sensitive | Use exact `mktoText` |
| `mktoButton` in email templates | Does not exist in Email 2.0 | Use table-based buttons with `mktoText` + variables |
| Local variable `${var}` in global `<style>` | Cannot resolve module scope | Use inline `style` for local variables |
| `mktoColor` default with RGB/named color | Must be 6-digit hex | Use `#rrggbb` format |
| `<span class="mktoText">` | Block content in inline element | Use `<div>` or `<td>` |
| Module IDs in CSS selectors | IDs change on duplication | Use classes for CSS targeting |

---

## 12. Validation Checklist

Use this checklist before approving any v2.0 template:

- [ ] **HTML validity:** All tags properly opened and closed
- [ ] **Single container:** Exactly one `class="mktoContainer"` element
- [ ] **Container content:** Only `mktoModule` elements as direct children of container (no stray HTML, comments, or whitespace nodes)
- [ ] **Container-module pairing:** Module element type matches container type (see §3.2)
- [ ] **No nested modules:** No `mktoModule` inside another `mktoModule`
- [ ] **Unique IDs:** Every `id` attribute is unique across the entire template
- [ ] **ID format:** Only letters, numbers, dashes, underscores in IDs
- [ ] **Case-sensitive classes:** `mktoText`, `mktoImg`, `mktoSnippet`, `mktoVideo`, `mktoModule`, `mktoContainer` (exact casing)
- [ ] **Required attributes:** All mkto elements have `id` and `mktoName` (except container which needs only `id`)
- [ ] **Variable defaults:** `mktoColor` uses 6-digit hex; `mktoNumber` has a numeric `default`; `mktoList` has `values`
- [ ] **Variable scope:** Local (`mktoModuleScope="true"`) variables NOT referenced in global `<style>`
- [ ] **Responsive CSS:** All media query rules include `!important`
- [ ] **CSS targeting:** No module IDs in CSS selectors; use classes instead
- [ ] **System tokens:** `{{system.unsubscribeLink}}` present in an accessible location
- [ ] **Link protocols:** All URLs include `https://`; variables include protocol in default value
- [ ] **Image alt text:** All `<img>` tags have `alt` attribute
- [ ] **Inline styles:** Desktop styles pre-inlined; `<style>` block used only for media queries and pseudo-classes

---

## 13. Troubleshooting Quick Reference

| Symptom | Likely Cause | Solution |
|---------|-------------|----------|
| "Invalid Module" error | Non-module content inside container, wrong module element type, unclosed tags | See §8.3 debugging steps |
| "Duplicate Element Id" | Two elements share same `id` | Find and rename duplicate |
| "Unused Variable" warning | `<meta>` declared but `${id}` never used | Remove unused meta or add reference |
| "Element With No Name" | Missing `mktoName` on mkto element | Add `mktoName` attribute |
| "Invalid Field Value" | Wrong format for variable default | Check type requirements (§4.2) |
| Module not showing in sidebar | `mktoActive="false"` | Set `mktoActive="true"` |
| Module on canvas but can't re-add if deleted | `mktoActive="false"` + `mktoAddByDefault="true"` | Set `mktoActive="true"` if re-adding should be allowed |
| Variable changes affect all modules | Variable is global scope | Add `mktoModuleScope="true"` |
| Variable not resolving in `<style>` | Local variable in global context | Move reference to inline `style` within module |
| Responsive CSS not working | Missing `!important` | Add `!important` to all media query rules |
| CSS breaks on duplicated modules | Targeting by ID | Switch to class selectors |
| Images not linkable | Using `<img class="mktoImg">` directly | Switch to `<div class="mktoImg">` wrapper pattern |
| Snippet tokens not resolving | Tokens inside `mktoSnippet` | Move tokens outside snippet to parent module |

---

## 14. Regex Validation Patterns

```javascript
// Validate template structure
const validationPatterns = {
  // Count containers (should be exactly 1)
  containerCount: (html) => (html.match(/class\s*=\s*["'][^"']*\bmktoContainer\b/gi) || []).length,

  // Check for duplicate IDs across all mkto elements
  findDuplicateIds: (html) => {
    const ids = [...html.matchAll(/(?:class\s*=\s*["'][^"']*\bmkto\w+\b[^"']*["'][^>]*\bid\s*=\s*["']([^"']+)["']|id\s*=\s*["']([^"']+)["'][^>]*class\s*=\s*["'][^"']*\bmkto\w+\b)/gi)]
      .map(m => m[1] || m[2]);
    return ids.filter((id, i) => ids.indexOf(id) !== i);
  },

  // Check for invalid ID characters
  invalidIds: (html) => {
    const ids = [...html.matchAll(/\bid\s*=\s*["']([^"']+)["']/gi)].map(m => m[1]);
    return ids.filter(id => /[^a-zA-Z0-9\-_]/.test(id));
  },

  // Check mktoColor defaults are valid hex
  invalidColorDefaults: (html) => {
    return [...html.matchAll(/<meta[^>]*class\s*=\s*["']mktoColor["'][^>]*default\s*=\s*["']([^"']+)["']/gi)]
      .filter(m => !/^#[0-9a-fA-F]{6}$/.test(m[1]))
      .map(m => m[1]);
  },

  // Check for case-sensitivity violations
  wrongCaseClasses: (html) => {
    const correct = ['mktoContainer', 'mktoModule', 'mktoText', 'mktoImg', 'mktoSnippet', 'mktoVideo'];
    const found = [...html.matchAll(/class\s*=\s*["']([^"']+)["']/gi)]
      .flatMap(m => m[1].split(/\s+/));
    return found.filter(cls =>
      correct.some(c => cls.toLowerCase() === c.toLowerCase() && cls !== c)
    );
  }
};
```

---

*Document compiled from official Adobe Marketo Engage documentation, Marketo Nation community posts, and email development best practices. Last updated: February 2026.*

