#!/usr/bin/env python3
"""
Validate a Marketo Email 2.0 template against standards.

Usage:
    python3 validate.py <template.html>

Output: JSON validation report with errors, warnings, and score
"""

import sys
import json
import re
import argparse
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

import parser_utils


def validate_template(file_path: str) -> dict:
    """
    Validate a Marketo template against Email 2.0 standards.

    Args:
        file_path: Path to the template HTML file

    Returns:
        Validation report dictionary
    """
    soup, html_str, _ = parser_utils.load_template(file_path)

    errors = []
    warnings = []

    # === CRITICAL ERRORS ===

    # Check 1: Exactly one container
    containers = soup.find_all(class_=re.compile(r'\bmktoContainer\b'))
    if len(containers) == 0:
        errors.append({
            'type': 'missing_container',
            'message': 'No mktoContainer found (template is not modular)'
        })
    elif len(containers) > 1:
        errors.append({
            'type': 'multiple_containers',
            'message': f'Found {len(containers)} mktoContainer elements (only 1 allowed)'
        })

    # Check 2: All IDs are unique
    id_map = parser_utils.get_all_ids(soup)
    for element_id, lines in id_map.items():
        if len(lines) > 1:
            errors.append({
                'type': 'duplicate_id',
                'message': f"ID '{element_id}' appears {len(lines)} times",
                'lines': lines
            })

    # Check 3: ID format validation
    invalid_id_pattern = re.compile(r'[^a-zA-Z0-9_-]')
    for element_id in id_map.keys():
        if invalid_id_pattern.search(element_id):
            line_num = id_map[element_id][0]
            errors.append({
                'type': 'invalid_id_format',
                'message': f"ID '{element_id}' contains invalid characters (only a-z, A-Z, 0-9, -, _ allowed)",
                'line': line_num
            })

    # Check 4: Required attributes on modules
    modules = parser_utils.find_modules(soup)
    for module in modules:
        module_id = module.get('id', '')
        if not module_id:
            errors.append({
                'type': 'missing_attribute',
                'message': 'Module missing required id attribute'
            })
        if not parser_utils.extract_module_name(module):
            line_num = parser_utils.find_element_line_number(html_str, module_id) if module_id else None
            errors.append({
                'type': 'missing_attribute',
                'message': f"Module '{module_id}' missing required mktoName attribute",
                'line': line_num
            })

    # Check 5: Required attributes on editable elements
    editable_elements = parser_utils.find_editable_elements(soup)
    for elem in editable_elements:
        elem_id = elem.get('id', '')
        elem_class = elem.get('class', [])
        elem_type = next((c for c in elem_class if c.startswith('mkto')), 'unknown')

        if not elem_id:
            errors.append({
                'type': 'missing_attribute',
                'message': f"{elem_type} element missing required id attribute"
            })
        if not parser_utils.extract_module_name(elem):
            line_num = parser_utils.find_element_line_number(html_str, elem_id) if elem_id else None
            errors.append({
                'type': 'missing_attribute',
                'message': f"{elem_type} element '{elem_id}' missing required mktoName attribute",
                'line': line_num
            })

    # === NON-CRITICAL WARNINGS ===

    # Check 6: Case sensitivity - warn only when attribute casing differs from canonical form
    case_checks = [
        ('mktoName', r'\bmktoname\s*='),
        ('mktoModuleScope', r'\bmktomodulescope\s*='),
        ('mktoImgLink', r'\bmktoimglink\s*='),
        ('mktoImgClass', r'\bmktoimgclass\s*='),
        ('mktoImgSrc', r'\bmktoimgsrc\s*='),
        ('mktoImgWidth', r'\bmktoimgwidth\s*='),
        ('mktoImgHeight', r'\bmktoimgheight\s*='),
        ('mktoLockImgSize', r'\bmktolockimgsize\s*='),
        ('mktoLockImgStyle', r'\bmktolockimgstyle\s*='),
        ('mktoAddByDefault', r'\bmktoaddbydefault\s*='),
    ]

    for correct, pattern in case_checks:
        for match in re.finditer(pattern, html_str, re.IGNORECASE):
            actual = match.group(0).split('=')[0].strip()
            if actual == correct:
                continue
            line_num = html_str[:match.start()].count('\n') + 1
            warnings.append({
                'type': 'case_sensitivity',
                'message': f"Found '{actual}' on line {line_num} (should be '{correct}')",
                'line': line_num
            })

    # Check 7: Unused variables (declared but not referenced)
    variables = parser_utils.find_variables(soup)
    body = soup.find('body')
    body_html = str(body) if body else ''

    for var in variables:
        var_id = var.get('id', '')
        if var_id and f'${{{var_id}}}' not in body_html:
            line_num = parser_utils.find_element_line_number(html_str, var_id)
            warnings.append({
                'type': 'unused_variable',
                'message': f"Variable '{var_id}' declared but never referenced",
                'line': line_num
            })

    # Check 8: Missing default values
    for var in variables:
        var_id = var.get('id', '')
        if not var.get('default'):
            line_num = parser_utils.find_element_line_number(html_str, var_id)
            warnings.append({
                'type': 'missing_default',
                'message': f"Variable '{var_id}' has no default value",
                'line': line_num
            })

    # === STATISTICS ===
    stats = {
        'modules': len(modules),
        'variables': len(variables),
        'unique_ids': len(id_map),
        'editable_elements': len(editable_elements),
        'containers': len(containers)
    }

    # === SCORE CALCULATION ===
    score = 100 - (len(errors) * 10) - len(warnings)
    score = max(0, min(100, score))

    valid = len(errors) == 0

    return {
        'valid': valid,
        'score': score,
        'errors': errors,
        'warnings': warnings,
        'stats': stats
    }


def main():
    parser = argparse.ArgumentParser(
        description='Validate a Marketo Email 2.0 template'
    )
    parser.add_argument('template', help='Path to the template HTML file')

    args = parser.parse_args()

    try:
        report = validate_template(args.template)
        print(json.dumps(report, indent=2))
    except FileNotFoundError:
        print(f"Error: File not found: {args.template}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
