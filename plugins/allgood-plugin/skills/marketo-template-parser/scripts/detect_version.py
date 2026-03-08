#!/usr/bin/env python3
"""
Detect Marketo template version (1.0 vs 2.0) and analyze structure.

For v1.0 templates: lists mktEditable regions, extracts {{my.tokens}},
and provides upgrade guidance for migrating to Email 2.0.

Usage:
    python3 detect_version.py <template.html>
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


def detect_version(file_path: str) -> dict:
    soup, html, lines = parser_utils.load_template(file_path)

    # Detect v2.0 markers
    has_container = bool(soup.find(class_=re.compile(r'mktoContainer', re.I)))
    has_modules = bool(soup.find(class_=re.compile(r'mktoModule', re.I)))
    has_meta_vars = bool(soup.find('meta', class_=re.compile(r'mkto', re.I)))

    # Detect v1.0 markers
    v1_editables = soup.find_all(class_='mktEditable')

    is_v2 = has_container or has_modules or has_meta_vars
    is_v1 = len(v1_editables) > 0 and not is_v2

    if is_v2:
        return {"version": "2.0", "message": "Email 2.0 template detected. Use list_modules.py and validate.py for analysis."}

    if not is_v1:
        return {"version": "unknown", "message": "No Marketo template markers found (no mktEditable, mktoModule, or mktoContainer)."}

    # Analyze v1.0 template
    regions = []
    for el in v1_editables:
        el_id = el.get('id', '')
        el_name = el.get('mktoname', el_id)
        el_html = str(el)
        line = parser_utils.get_line_number(html, f'id="{el_id}"') or 0

        # Extract {{my.Token}} references within this region
        tokens = sorted(set(re.findall(r'\{\{my\.([^}:]+)', el_html)))

        regions.append({
            "id": el_id,
            "name": el_name,
            "line": line,
            "tokens": tokens,
            "html_lines": el_html.count('\n') + 1
        })

    # All tokens across entire template
    all_tokens = sorted(set(re.findall(r'\{\{my\.([^}:]+)', html)))

    result = {
        "version": "1.0",
        "regions": regions,
        "region_count": len(regions),
        "tokens": all_tokens,
        "token_count": len(all_tokens),
        "upgrade": {
            "summary": "This is a Marketo Email 1.0 template. Email 2.0 adds modular structure, variables, and drag-and-drop editing.",
            "steps": [
                "1. Add a mktoContainer wrapper: <table class=\"mktoContainer\" id=\"container\">",
                "2. Convert each mktEditable div to a mktoModule: <tr class=\"mktoModule\" id=\"moduleId\" mktoName=\"Module Name\">",
                "3. Replace {{my.Token}} references with <meta> variable declarations in <head>",
                "4. Add mktoName attributes to all modules and editable elements",
                "5. Use mktoText, mktoImg, mktoSnippet classes for editable content areas",
                "6. Validate with: python3 scripts/validate.py <template.html>"
            ],
            "region_mapping": [
                {
                    "v1_id": r["id"],
                    "v1_name": r["name"],
                    "suggested_v2": f'<tr class="mktoModule" id="{r["id"]}" mktoName="{r["name"]}">',
                    "tokens_to_convert": r["tokens"]
                }
                for r in regions
            ]
        }
    }

    return result


def main():
    parser = argparse.ArgumentParser(description='Detect Marketo template version')
    parser.add_argument('template', help='Path to Marketo template HTML file')
    args = parser.parse_args()

    if not Path(args.template).exists():
        print(f"Error: File not found: {args.template}", file=sys.stderr)
        sys.exit(1)

    result = detect_version(args.template)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
