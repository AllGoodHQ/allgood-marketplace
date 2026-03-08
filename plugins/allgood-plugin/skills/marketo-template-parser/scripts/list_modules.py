#!/usr/bin/env python3
"""
List all modules in a Marketo Email 2.0 template.

Usage:
    python3 list_modules.py <template.html>
    python3 list_modules.py <template.html> --no-line-numbers

Output: JSON array of modules with id, name, and line number
"""

import sys
import json
import argparse
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Check for dependencies
try:
    import parser_utils
except ImportError as e:
    print(f"Error: Missing dependency - {e}", file=sys.stderr)
    print("Run: pip3 install beautifulsoup4", file=sys.stderr)
    sys.exit(1)


def list_modules(file_path: str, include_line_numbers: bool = True) -> list:
    """
    Extract all modules from a Marketo template.

    Args:
        file_path: Path to the template HTML file
        include_line_numbers: Whether to include line numbers

    Returns:
        List of module dictionaries
    """
    soup, html_str, _ = parser_utils.load_template(file_path)
    modules = parser_utils.find_modules(soup)

    result = []

    for module in modules:
        module_id = module.get('id', '')
        module_name = parser_utils.extract_module_name(module)

        module_data = {
            'id': module_id,
            'name': module_name
        }

        if include_line_numbers and module_id:
            line_num = parser_utils.find_element_line_number(html_str, module_id)
            module_data['line'] = line_num

        result.append(module_data)

    # Sort by line number if available
    if include_line_numbers:
        result.sort(key=lambda x: x.get('line', 0))

    return result


def main():
    parser = argparse.ArgumentParser(
        description='List all modules in a Marketo Email 2.0 template'
    )
    parser.add_argument('template', help='Path to the template HTML file')
    parser.add_argument(
        '--no-line-numbers',
        action='store_true',
        help='Exclude line numbers from output'
    )

    args = parser.parse_args()

    try:
        modules = list_modules(args.template, include_line_numbers=not args.no_line_numbers)
        print(json.dumps(modules, indent=2))
    except FileNotFoundError:
        print(f"Error: File not found: {args.template}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
