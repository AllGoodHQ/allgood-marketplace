#!/usr/bin/env python3
"""
Extract a specific module from a Marketo Email 2.0 template.

Usage:
    python3 get_module.py <template.html> <module_id>
    python3 get_module.py <template.html> <module_id> --no-styles
    python3 get_module.py <template.html> <module_id> --summary

Output: HTML content of the module (or JSON summary if --summary flag used)
"""

import sys
import json
import argparse
import re
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

import parser_utils


def get_module(file_path: str, module_id: str, strip_styles: bool = False) -> str:
    """
    Extract a specific module's HTML content.

    Args:
        file_path: Path to the template HTML file
        module_id: ID of the module to extract
        strip_styles: Whether to remove <style> tags

    Returns:
        HTML string of the module
    """
    soup, _, _ = parser_utils.load_template(file_path)

    # Find the module by ID
    module = soup.find(id=module_id)

    if not module:
        raise ValueError(f"Module with id '{module_id}' not found")

    # Check if it's actually a module
    classes = module.get('class', [])
    if not any('mktoModule' in cls for cls in classes):
        raise ValueError(f"Element '{module_id}' is not a mktoModule")

    # Strip styles if requested
    if strip_styles:
        module = parser_utils.strip_styles_from_element(module)

    return parser_utils.get_element_html(module)


def get_module_summary(file_path: str, module_id: str) -> dict:
    """
    Get a JSON summary of a module instead of full HTML.

    Args:
        file_path: Path to the template HTML file
        module_id: ID of the module to extract

    Returns:
        Dictionary with module summary including detailed element info
    """
    soup, html_str, _ = parser_utils.load_template(file_path)

    # Find the module by ID
    module = soup.find(id=module_id)

    if not module:
        raise ValueError(f"Module with id '{module_id}' not found")

    # Get module info
    module_name = parser_utils.extract_module_name(module)
    module_html = parser_utils.get_element_html(module)
    add_by_default = parser_utils.get_module_add_by_default(module)

    # Find all editable elements within this module
    editable_pattern = re.compile(r'\bmkto(Text|Img|Snippet|Video)\b')
    mkto_elements = module.find_all(class_=editable_pattern)
    cta_elements = module.find_all(class_=re.compile(r'\bcta\b'))
    seen = {}
    for elem in mkto_elements + cta_elements:
        eid = elem.get('id', id(elem))
        if eid not in seen:
            seen[eid] = elem
    all_editable = list(seen.values())

    # Extract detailed info for each editable element
    editable_details = []
    for elem in all_editable:
        info = parser_utils.extract_editable_element_info(elem)
        if info['id']:  # Only include elements with IDs
            editable_details.append(info)

    # Sort by ID for consistency
    editable_details.sort(key=lambda x: x['id'])

    # Get unique types for backwards compatibility
    editable_types = sorted(set([e['type'] for e in editable_details]))

    # Find variable references
    variable_pattern = re.compile(r'\$\{([a-zA-Z0-9_-]+)\}')
    variable_refs = variable_pattern.findall(module_html)
    unique_var_refs = sorted(set(variable_refs))

    # Build variable details with type/default metadata from <head> declarations
    var_lookup = parser_utils.build_variable_lookup(soup)
    variable_details = []
    for var_id in unique_var_refs:
        detail = {'id': var_id}
        if var_id in var_lookup:
            detail['type'] = var_lookup[var_id]['type']
            detail['default'] = var_lookup[var_id]['default']
        variable_details.append(detail)

    return {
        'id': module_id,
        'name': module_name,
        'line': parser_utils.find_element_line_number(html_str, module_id),
        'add_by_default': add_by_default,
        'editable_elements': len(editable_details),
        'editable_types': editable_types,
        'editable_details': editable_details,
        'variable_references': unique_var_refs,
        'variable_details': variable_details,
        'html_size': len(module_html),
        'html_lines': module_html.count('\n') + 1
    }


def main():
    parser = argparse.ArgumentParser(
        description='Extract a specific module from a Marketo Email 2.0 template'
    )
    parser.add_argument('template', help='Path to the template HTML file')
    parser.add_argument('module_id', help='ID of the module to extract')
    parser.add_argument(
        '--no-styles',
        action='store_true',
        help='Strip <style> tags from output'
    )
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Output JSON summary instead of HTML'
    )

    args = parser.parse_args()

    try:
        if args.summary:
            summary = get_module_summary(args.template, args.module_id)
            print(json.dumps(summary, indent=2))
        else:
            module_html = get_module(args.template, args.module_id, args.no_styles)
            print(module_html)
    except FileNotFoundError:
        print(f"Error: File not found: {args.template}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
