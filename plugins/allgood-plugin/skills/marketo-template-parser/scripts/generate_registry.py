#!/usr/bin/env python3
"""
Generate a JSON module registry from a Marketo Email 2.0 template.

Pure data extraction (no LLM needed). Output matches the schema used by
email-variant-generator/module-registry.json.

Usage:
    python3 scripts/generate_registry.py <template.html>

Output: Writes <template>-registry.json to the current directory.
"""

import json
import re
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

import parser_utils
from list_modules import list_modules
from get_module import get_module_summary


def generate_registry(file_path: str) -> dict:
    """
    Build a module registry from a Marketo template.

    Args:
        file_path: Path to the template HTML file

    Returns:
        Dictionary mapping module IDs to {elements, variables, content_variables, style_variables}
    """
    soup, html_str, _ = parser_utils.load_template(file_path)
    modules = parser_utils.find_modules(soup)
    var_lookup = parser_utils.build_variable_lookup(soup)

    registry = {}

    for module in modules:
        module_id = module.get('id', '')
        if not module_id:
            continue

        # Find editable elements within this module
        editable_pattern = re.compile(r'\bmkto(Text|Img|Snippet|Video)\b')
        mkto_elements = module.find_all(class_=editable_pattern)
        cta_elements = module.find_all(class_=re.compile(r'\bcta\b'))

        # Deduplicate by id
        seen = {}
        for elem in mkto_elements + cta_elements:
            eid = elem.get('id', id(elem))
            if eid not in seen:
                seen[eid] = elem

        # Build elements dict: htmlId -> elementType
        elements = {}
        for elem in seen.values():
            elem_id = elem.get('id', '')
            if not elem_id:
                continue
            info = parser_utils.extract_editable_element_info(elem)
            elements[elem_id] = info['type']

        # Sort elements by key for stable output
        elements = dict(sorted(elements.items()))

        # Find variable references in module HTML
        module_html = parser_utils.get_element_html(module)
        variable_pattern = re.compile(r'\$\{([a-zA-Z0-9_-]+)\}')
        variable_refs = sorted(set(variable_pattern.findall(module_html)))

        # Split variables into content vs style
        content_vars = []
        style_vars = []
        for var_id in variable_refs:
            var_info = var_lookup.get(var_id, {})
            if parser_utils.is_style_variable(var_id, var_info):
                style_vars.append(var_id)
            else:
                content_vars.append(var_id)

        registry[module_id] = {
            'addByDefault': parser_utils.get_module_add_by_default(module),
            'elements': elements,
            'content_variables': content_vars,
            'style_variables': style_vars,
        }

    return registry


def validate_registry(file_path: str, registry: dict) -> bool:
    """
    Cross-check registry against list_modules and get_module --summary.

    Args:
        file_path: Path to the template HTML file
        registry: The generated registry dict

    Returns:
        True if validation passed, False otherwise
    """
    errors = []

    # Check module count and names against list_modules
    modules_list = list_modules(file_path)
    list_ids = {m['id'] for m in modules_list}
    registry_ids = set(registry.keys())

    if len(modules_list) != len(registry):
        errors.append(
            f"Module count mismatch: list_modules={len(modules_list)}, registry={len(registry)}"
        )

    missing_from_registry = list_ids - registry_ids
    if missing_from_registry:
        errors.append(f"Modules in list_modules but not in registry: {missing_from_registry}")

    extra_in_registry = registry_ids - list_ids
    if extra_in_registry:
        errors.append(f"Modules in registry but not in list_modules: {extra_in_registry}")

    # Cross-check element counts per module against get_module --summary
    total_elements = 0
    for module_id, entry in registry.items():
        total_elements += len(entry['elements'])
        try:
            summary = get_module_summary(file_path, module_id)
            if summary['editable_elements'] != len(entry['elements']):
                errors.append(
                    f"Element count mismatch for {module_id}: "
                    f"summary={summary['editable_elements']}, registry={len(entry['elements'])}"
                )
        except ValueError:
            errors.append(f"Could not get summary for module: {module_id}")

    if errors:
        print("Validation FAILED:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return False

    print(
        f"Validated: {len(registry)} modules, {total_elements} elements, registry OK",
        file=sys.stderr,
    )
    return True


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/generate_registry.py <template.html>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    template_name = Path(file_path).stem

    if not Path(file_path).exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Generating registry for {file_path}...", file=sys.stderr)

    registry = generate_registry(file_path)

    # Write output
    output_file = f"{template_name}-registry.json"
    with open(output_file, 'w') as f:
        json.dump(registry, f, indent=2)
        f.write('\n')

    print(f"Wrote {output_file}", file=sys.stderr)

    # Validate
    if not validate_registry(file_path, registry):
        sys.exit(1)


if __name__ == '__main__':
    main()
