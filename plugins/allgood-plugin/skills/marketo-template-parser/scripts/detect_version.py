#!/usr/bin/env python3
"""
Detect Marketo template version (1.0 vs 2.0).

Lightweight version gate — run this first on an unknown template to decide
whether the rest of the skill's scripts (which target Email 2.0) apply.

Returns JSON with `version` ("1.0", "2.0", or "unknown") and a message.
For v1.0 templates, also reports region_count and token_count so the model
has quick context for framing the upgrade conversation.

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

    # Count regions and tokens — enough context without the full migration guide
    token_count = len(set(re.findall(r'\{\{my\.([^}:]+)', html)))

    return {
        "version": "1.0",
        "message": (
            "This template uses Email 1.0 (mktEditable regions + {{my.Token}}). "
            "Email 2.0 uses a different paradigm (mktoContainer + mktoModule + <meta> "
            "variables + ${variableId}). This skill targets 2.0 — upgrade the template "
            "before using the other scripts. For upgrade guidance, see "
            "references/marketo-template-reference.md."
        ),
        "region_count": len(v1_editables),
        "token_count": token_count,
    }


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
