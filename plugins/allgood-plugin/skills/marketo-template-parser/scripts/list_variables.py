#!/usr/bin/env python3
"""
List all variable declarations in a Marketo Email 2.0 template.

Usage:
    python3 list_variables.py <template.html>
    python3 list_variables.py <template.html> --type mktoColor
    python3 list_variables.py <template.html> --scope global

Output: JSON object with {global: [...], module: [...]}
"""

import sys
import json
import argparse
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

import parser_utils


def list_variables(
    file_path: str,
    var_type: str = None,
    scope: str = None
) -> dict:
    """
    Extract all variable declarations from a Marketo template.

    Args:
        file_path: Path to the template HTML file
        var_type: Filter by variable type (mktoString, mktoColor, etc.)
        scope: Filter by scope ('global' or 'module')

    Returns:
        Dictionary with 'global' and 'module' arrays
    """
    soup, html_str, _ = parser_utils.load_template(file_path)
    variables = parser_utils.find_variables(soup)

    result = {
        'global': [],
        'module': []
    }

    for var in variables:
        var_id = var.get('id', '')
        var_type_cls = parser_utils.extract_variable_type(var)
        var_name = var.get('mktoName') or var.get('mktoname', '')
        var_default = var.get('default', '')
        is_module = parser_utils.is_module_scoped(var)

        # Apply type filter
        if var_type and var_type_cls != var_type:
            continue

        # Apply scope filter
        if scope == 'global' and is_module:
            continue
        if scope == 'module' and not is_module:
            continue

        var_data = {
            'id': var_id,
            'type': var_type_cls,
            'name': var_name,
            'default': var_default
        }

        # Add line number
        if var_id:
            line_num = parser_utils.find_element_line_number(html_str, var_id)
            var_data['line'] = line_num

        # Add to appropriate scope
        if is_module:
            result['module'].append(var_data)
        else:
            result['global'].append(var_data)

    # Sort by line number
    result['global'].sort(key=lambda x: x.get('line', 0))
    result['module'].sort(key=lambda x: x.get('line', 0))

    return result


def main():
    parser = argparse.ArgumentParser(
        description='List all variables in a Marketo Email 2.0 template'
    )
    parser.add_argument('template', help='Path to the template HTML file')
    parser.add_argument(
        '--type',
        choices=['mktoString', 'mktoColor', 'mktoBoolean', 'mktoNumber', 'mktoList', 'mktoHTML', 'mktoImg'],
        help='Filter by variable type'
    )
    parser.add_argument(
        '--scope',
        choices=['global', 'module'],
        help='Filter by scope (global or module-scoped)'
    )

    args = parser.parse_args()

    try:
        variables = list_variables(args.template, args.type, args.scope)
        print(json.dumps(variables, indent=2))
    except FileNotFoundError:
        print(f"Error: File not found: {args.template}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
