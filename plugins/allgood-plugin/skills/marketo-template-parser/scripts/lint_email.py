#!/usr/bin/env python3
"""
Lint HTML email for rendering issues across major clients.

Checks structure, images, links, styles, accessibility, Gmail/Outlook
compatibility, and dark mode readiness. Works on any email HTML (v1.0, v2.0,
or plain email — not Marketo-specific).

Usage:
    python3 lint_email.py <email.html>
    python3 lint_email.py <email.html> --category accessibility gmail
    python3 lint_email.py <email.html> --category outlook darkmode
"""

import sys
import json
import re
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    import parser_utils
except ImportError as e:
    print(f"Error: Missing dependency - {e}", file=sys.stderr)
    print("Run: pip3 install beautifulsoup4", file=sys.stderr)
    sys.exit(1)

ALL_CATEGORIES = [
    'structure', 'images', 'styles', 'links', 'tables',
    'accessibility', 'size', 'outlook', 'gmail', 'darkmode'
]


def _get_line(html_str, pos):
    """Get 1-indexed line number from character position."""
    return html_str[:pos].count('\n') + 1


def _get_inline_style(el):
    """Get inline style string from element."""
    return el.get('style', '') or ''


def _find_in_style(style_str, pattern):
    """Check if a regex pattern matches in an inline style string."""
    return bool(re.search(pattern, style_str, re.IGNORECASE))


def _parse_font_size_px(style_str):
    """Extract font-size in px from inline style. Returns None if not found or not in px."""
    m = re.search(r'font-size:\s*(\d+(?:\.\d+)?)\s*px', style_str, re.IGNORECASE)
    return float(m.group(1)) if m else None


def lint_email(file_path, categories=None):
    soup, html_str, lines = parser_utils.load_template(file_path)
    categories = set(categories or ALL_CATEGORIES)
    issues = []

    def add(rule_id, severity, message, line=None, element=None, category=None):
        if category and category not in categories:
            return
        issue = {'id': rule_id, 'severity': severity, 'message': message}
        if line:
            issue['line'] = line
        if element:
            issue['element'] = element
        issues.append(issue)

    # ===================== PASS 1: DOM RULES =====================

    # --- Structure ---
    if 'structure' in categories:
        # STRUCT-001: DOCTYPE
        if not html_str.lstrip().lower().startswith('<!doctype'):
            add('STRUCT-001', 'error', 'Missing <!DOCTYPE> declaration', line=1, category='structure')

        # STRUCT-002: html lang
        html_tag = soup.find('html')
        if html_tag and not html_tag.get('lang'):
            add('STRUCT-002', 'error', '<html> missing lang attribute (screen readers need this)', category='structure')
        elif not html_tag:
            add('STRUCT-002', 'error', 'No <html> element found', category='structure')

        # STRUCT-003: charset meta
        charset_meta = soup.find('meta', attrs={'charset': True})
        content_type_meta = soup.find('meta', attrs={'http-equiv': re.compile(r'content-type', re.I)})
        if not charset_meta and not content_type_meta:
            add('STRUCT-003', 'warning', 'No charset meta tag found', category='structure')

    # --- Images ---
    if 'images' in categories:
        for img in soup.find_all('img'):
            img_id = img.get('id', img.get('src', '')[:40])
            src = img.get('src', '')
            line = parser_utils.get_line_number(html_str, src) if src else None

            # IMG-001: alt attribute
            if img.get('alt') is None:
                add('IMG-001', 'error', f'<img> missing alt attribute (src: {src[:60]})',
                    line=line, element=img_id, category='images')

            # IMG-002: width + height HTML attributes
            if not img.get('width') or not img.get('height'):
                add('IMG-002', 'warning', f'<img> missing HTML width/height attributes — Outlook ignores CSS sizing (src: {src[:60]})',
                    line=line, element=img_id, category='images')

            # IMG-003: SVG
            if src and '.svg' in src.lower():
                add('IMG-003', 'warning', f'SVG image not supported in Outlook (src: {src[:60]})',
                    line=line, element=img_id, category='images')

            # IMG-004: HTTPS
            if src and src.startswith('http://'):
                add('IMG-004', 'warning', f'Image uses HTTP instead of HTTPS (src: {src[:60]})',
                    line=line, element=img_id, category='images')

        # SVG elements
        for svg in soup.find_all('svg'):
            add('IMG-003', 'warning', 'Inline <svg> element — not supported in Outlook', category='images')

    # --- Links ---
    if 'links' in categories:
        for a in soup.find_all('a'):
            href = a.get('href', '')
            a_text = a.get_text(strip=True)
            a_id = a.get('id', a_text[:30] if a_text else href[:30])

            # LINK-001: href present
            if not href:
                add('LINK-001', 'error', f'<a> tag missing href attribute',
                    element=a_id, category='links')
                continue

            # LINK-002: no javascript:
            if href.lower().startswith('javascript:'):
                add('LINK-002', 'error', f'javascript: link found (href: {href[:60]})',
                    element=a_id, category='links')

            # LINK-003: HTTPS
            if href.startswith('http://') and not href.startswith('http://schemas'):
                add('LINK-003', 'warning', f'Link uses HTTP instead of HTTPS (href: {href[:60]})',
                    element=a_id, category='links')

            # LINK-004: visible content
            child_imgs = a.find_all('img')
            has_img_alt = any(img.get('alt') for img in child_imgs)
            if not a_text and not has_img_alt:
                add('LINK-004', 'warning', f'<a> has no visible text or img with alt (href: {href[:60]})',
                    element=a_id, category='links')

    # --- Tables ---
    if 'tables' in categories:
        for table in soup.find_all('table'):
            table_id = table.get('id', '')
            has_th = bool(table.find('th'))
            role = table.get('role', '')

            # TBL-001: layout tables need role="presentation"
            if not has_th and role not in ('presentation', 'none'):
                add('TBL-001', 'warning', f'Layout table missing role="presentation" — screen readers announce table structure',
                    element=table_id, category='tables')

            # TBL-002: nesting depth
            depth = 0
            parent = table.parent
            while parent:
                if parent.name == 'table':
                    depth += 1
                parent = parent.parent if hasattr(parent, 'parent') else None
            if depth > 3:
                add('TBL-002', 'warning', f'Table nested {depth} levels deep (max 3 recommended)',
                    element=table_id, category='tables')

    # --- Styles (DOM) ---
    if 'styles' in categories:
        # STYLE-004: external stylesheets
        for link in soup.find_all('link', rel='stylesheet'):
            add('STYLE-004', 'error', f'External stylesheet found — not supported in email (href: {link.get("href", "")[:60]})',
                category='styles')

        # STYLE-005: @import
        for style in soup.find_all('style'):
            if style.string and '@import' in style.string:
                add('STYLE-005', 'error', '@import found in <style> block — not supported in email',
                    category='styles')

        # STYLE-006: JavaScript
        for script in soup.find_all('script'):
            add('STYLE-006', 'error', '<script> element found — JavaScript not supported in email',
                category='styles')
        for el in soup.find_all(attrs={'onclick': True}):
            add('STYLE-006', 'error', f'onclick handler found on <{el.name}> — JavaScript not supported',
                element=el.get('id', ''), category='styles')
        for a in soup.find_all('a', href=re.compile(r'^javascript:', re.I)):
            pass  # Already caught by LINK-002

    # ===================== PASS 2: CSS/INLINE-STYLE RULES =====================

    if 'styles' in categories:
        banned_css = re.compile(r'\b(float|position)\s*:', re.I)
        banned_display = re.compile(r'display\s*:\s*(flex|grid)', re.I)

        for el in soup.find_all(style=True):
            style = _get_inline_style(el)
            el_id = el.get('id', f'<{el.name}>')

            # STYLE-001: banned CSS
            if banned_css.search(style):
                prop = banned_css.search(style).group(1)
                add('STYLE-001', 'warning', f'CSS "{prop}" in inline style — ignored by Outlook ({el_id})',
                    element=el_id, category='styles')
            if banned_display.search(style):
                val = banned_display.search(style).group(1)
                add('STYLE-001', 'warning', f'display:{val} in inline style — ignored by Outlook ({el_id})',
                    element=el_id, category='styles')

            # STYLE-003: !important in inline styles
            if '!important' in style:
                add('STYLE-003', 'warning', f'!important in inline style — Outlook ignores entire declaration ({el_id})',
                    element=el_id, category='styles')

    if 'accessibility' in categories:
        # TYPO-001: font-family generic fallback
        generic_fallbacks = {'serif', 'sans-serif', 'monospace', 'cursive', 'fantasy', 'system-ui'}
        for el in soup.find_all(style=re.compile(r'font-family', re.I)):
            style = _get_inline_style(el)
            m = re.search(r'font-family:\s*([^;]+)', style, re.I)
            if m:
                fonts = [f.strip().strip("'\"").lower() for f in m.group(1).split(',')]
                if fonts and fonts[-1] not in generic_fallbacks:
                    add('TYPO-001', 'warning', f'font-family missing generic fallback (ends with "{fonts[-1]}")',
                        element=el.get('id', f'<{el.name}>'), category='accessibility')

        # TYPO-002: font-size >= 14px
        for el in soup.find_all(style=re.compile(r'font-size', re.I)):
            if el.name in ('p', 'td', 'div', 'span', 'li'):
                size = _parse_font_size_px(_get_inline_style(el))
                if size is not None and size < 14:
                    add('TYPO-002', 'warning', f'Font size {size}px below 14px minimum ({el.get("id", f"<{el.name}>")})',
                        element=el.get('id', f'<{el.name}>'), category='accessibility')

    # ===================== PASS 3: SIZE + GMAIL RULES =====================

    if 'size' in categories:
        html_bytes = len(html_str.encode('utf-8'))

        # SIZE-001: 102KB hard limit
        if html_bytes > 102400:
            add('SIZE-001', 'error', f'HTML is {html_bytes // 1024}KB — Gmail clips at 102KB (footers, tracking pixels lost)',
                category='size')
        # SIZE-002: 85KB safety margin
        elif html_bytes > 87040:
            add('SIZE-002', 'warning', f'HTML is {html_bytes // 1024}KB — close to Gmail 102KB clip limit (ESP tracking adds ~10-15KB)',
                category='size')

    if 'gmail' in categories:
        head = soup.find('head')
        body = soup.find('body')

        # GMAIL-001: style blocks in head
        if body:
            for style in body.find_all('style'):
                add('GMAIL-001', 'error', '<style> block in <body> — Gmail only supports <style> in <head>',
                    category='gmail')

        # GMAIL-002: style block size
        for style in soup.find_all('style'):
            if style.string and len(style.string) > 8192:
                add('GMAIL-002', 'warning', f'<style> block exceeds 8,192 chars ({len(style.string)} chars) — Gmail strips entire block plus all subsequent blocks',
                    category='gmail')

        # GMAIL-003: background-image in style blocks
        for style in soup.find_all('style'):
            if style.string and re.search(r'background-image\s*:\s*url\s*\(', style.string, re.I):
                add('GMAIL-003', 'warning', 'background-image: url() inside <style> block — Gmail strips entire block. Use inline styles instead.',
                    category='gmail')

        # GMAIL-004: attribute selectors
        for style in soup.find_all('style'):
            if style.string and re.search(r'\[\s*(class|id|href|src)\s*[=~|^$*]', style.string, re.I):
                add('GMAIL-004', 'warning', 'Attribute selector in <style> block — Gmail strips these. Use class selectors (.foo) instead.',
                    category='gmail')

    # ===================== PASS 4: OUTLOOK + DARK MODE =====================

    if 'outlook' in categories:
        # MSO-001: padding on <a> tags
        for a in soup.find_all('a', style=re.compile(r'padding', re.I)):
            style = _get_inline_style(a)
            if _find_in_style(style, r'padding'):
                a_id = a.get('id', a.get_text(strip=True)[:30])
                add('MSO-001', 'warning', f'Padding on <a> tag — Outlook ignores this. Apply padding to parent <td> instead.',
                    element=a_id, category='outlook')

        # MSO-002: img with CSS size but no HTML attrs
        for img in soup.find_all('img', style=re.compile(r'(width|height)', re.I)):
            if not img.get('width') or not img.get('height'):
                src = img.get('src', '')[:40]
                add('MSO-002', 'warning', f'<img> has CSS width/height but no HTML attributes — Outlook ignores CSS sizing (src: {src})',
                    element=img.get('id', src), category='outlook')

        # MSO-003: VML requires xmlns
        has_vml = bool(re.search(r'<v:(rect|fill|background|roundrect|textbox)', html_str, re.I))
        if has_vml:
            html_tag = soup.find('html')
            if html_tag and not html_tag.get('xmlns:v'):
                add('MSO-003', 'warning', 'VML elements found but <html> missing xmlns:v="urn:schemas-microsoft-com:vml"',
                    category='outlook')

        # MSO-004: no <button> elements
        for btn in soup.find_all('button'):
            add('MSO-004', 'error', '<button> element found — not supported in email. Use styled <a> in <td> instead.',
                category='outlook')

    if 'darkmode' in categories:
        # DM-001: containers declare both bg and text color
        for el in soup.find_all(['table', 'td', 'div'], style=True):
            style = _get_inline_style(el)
            has_bg = _find_in_style(style, r'background(-color)?\s*:')
            has_color = _find_in_style(style, r'(?<!background-)color\s*:')
            if has_bg and not has_color:
                add('DM-001', 'warning', f'Element has background-color but no text color — dark mode may invert unpredictably',
                    element=el.get('id', f'<{el.name}>'), category='darkmode')

        # DM-002: pure white/black
        pure_colors = re.compile(r'(?:color|background(?:-color)?)\s*:\s*(?:#fff(?:fff)?|#000(?:000)?|white|black)\b', re.I)
        for m in pure_colors.finditer(html_str):
            line = _get_line(html_str, m.start())
            add('DM-002', 'warning', f'Pure white/black color ({m.group()}) — use off-values (#FAFAFA/#111111) to reduce aggressive dark mode inversion',
                line=line, category='darkmode')

        # DM-003: dark mode meta without CSS
        color_scheme_meta = soup.find('meta', attrs={'name': re.compile(r'color-scheme', re.I)})
        has_dark_css = bool(re.search(r'prefers-color-scheme\s*:\s*dark', html_str, re.I))
        if color_scheme_meta and not has_dark_css:
            add('DM-003', 'warning', 'Dark mode meta tag present but no @media (prefers-color-scheme: dark) CSS — Apple Mail will apply partial inversion',
                category='darkmode')

        # DM-004: PNG logos without dark mode protection
        # Check first few images (likely logos) for .png without swap pattern
        imgs = soup.find_all('img', src=re.compile(r'\.png', re.I))
        for img in imgs[:3]:
            src = img.get('src', '')
            parent = img.parent
            # Check if there's a sibling or nearby dark-mode swap image
            if parent:
                siblings = parent.find_all('img')
                if len(siblings) < 2:
                    classes = ' '.join(img.get('class', []))
                    if 'dark' not in classes.lower() and 'light' not in classes.lower():
                        add('DM-004', 'warning', f'PNG image near top of email (likely logo) without dark-mode image swap — may disappear on dark backgrounds (src: {src[:60]})',
                            element=img.get('id', ''), category='darkmode')

    # --- Accessibility extras ---
    if 'accessibility' in categories:
        # A11Y-001: links underlined
        for a in soup.find_all('a', style=re.compile(r'text-decoration', re.I)):
            style = _get_inline_style(a)
            if _find_in_style(style, r'text-decoration\s*:\s*none'):
                href = a.get('href', '')
                # Skip if it looks like a button (has background-color)
                if not _find_in_style(style, r'background(-color)?\s*:'):
                    add('A11Y-001', 'warning', f'Link with text-decoration:none — underline links for accessibility',
                        element=a.get('id', href[:30]), category='accessibility')

        # A11Y-002: line-height >= 1.5x font-size
        for el in soup.find_all(style=re.compile(r'line-height', re.I)):
            style = _get_inline_style(el)
            font_size = _parse_font_size_px(style)
            lh_match = re.search(r'line-height:\s*(\d+(?:\.\d+)?)\s*px', style, re.I)
            if font_size and lh_match:
                lh = float(lh_match.group(1))
                if lh < font_size * 1.5:
                    add('A11Y-002', 'warning', f'line-height ({lh}px) less than 1.5x font-size ({font_size}px)',
                        element=el.get('id', f'<{el.name}>'), category='accessibility')

        # A11Y-003: heading hierarchy
        headings = []
        for h in soup.find_all(re.compile(r'^h[1-6]$')):
            level = int(h.name[1])
            headings.append(level)
        for i in range(1, len(headings)):
            if headings[i] > headings[i - 1] + 1:
                add('A11Y-003', 'error', f'Heading hierarchy skips from h{headings[i-1]} to h{headings[i]}',
                    category='accessibility')

        # A11Y-004: no title on interactive elements
        for el in soup.find_all(['a', 'button'], attrs={'title': True}):
            add('A11Y-004', 'warning', f'title attribute on <{el.name}> — screen readers may read both title and text',
                element=el.get('id', ''), category='accessibility')

    # ===================== SCORING =====================

    error_count = sum(1 for i in issues if i['severity'] == 'error')
    warning_count = sum(1 for i in issues if i['severity'] == 'warning')
    info_count = sum(1 for i in issues if i['severity'] == 'info')

    score = 100 - (error_count * 5) - (warning_count * 2)
    score = max(0, min(100, score))

    return {
        'issues': issues,
        'summary': {
            'errors': error_count,
            'warnings': warning_count,
            'info': info_count,
            'total': len(issues),
            'categories_checked': sorted(categories)
        },
        'score': score
    }


def main():
    parser = argparse.ArgumentParser(description='Lint HTML email for rendering issues')
    parser.add_argument('email', help='Path to HTML email file')
    parser.add_argument('--category', nargs='+', choices=ALL_CATEGORIES,
                        help='Only check specific categories')

    args = parser.parse_args()

    if not Path(args.email).exists():
        print(f"Error: File not found: {args.email}", file=sys.stderr)
        sys.exit(1)

    result = lint_email(args.email, args.category)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
