"""
Shared utilities for parsing Marketo Email 2.0 templates.
"""

import re
import sys
from typing import Dict, List, Optional, Tuple

try:
    from bs4 import BeautifulSoup, Comment
except ImportError:
    print("Error: beautifulsoup4 required. Install: pip3 install beautifulsoup4", file=sys.stderr)
    sys.exit(1)


def load_template(file_path: str) -> Tuple[BeautifulSoup, str, List[str]]:
    """
    Load and parse a Marketo template HTML file.

    Args:
        file_path: Path to the HTML template file

    Returns:
        Tuple of (BeautifulSoup object, raw HTML string, list of lines)
    """
    for encoding in ('utf-8', 'latin-1'):
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                html = f.read()
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError(f"Cannot decode {file_path} (tried utf-8, latin-1)")

    soup = BeautifulSoup(html, 'html.parser')
    lines = html.split('\n')

    return soup, html, lines


def get_line_number(html_str: str, search_str: str, occurrence: int = 1) -> Optional[int]:
    """
    Find the line number where a substring appears in HTML.

    Args:
        html_str: Full HTML content
        search_str: String to search for
        occurrence: Which occurrence to find (1-indexed)

    Returns:
        Line number (1-indexed) or None if not found
    """
    lines = html_str.split('\n')
    count = 0

    for i, line in enumerate(lines, start=1):
        if search_str in line:
            count += 1
            if count == occurrence:
                return i

    return None


def find_element_line_number(html_str: str, element_id: str) -> Optional[int]:
    """
    Find the line number where an element with a specific ID appears.

    Args:
        html_str: Full HTML content
        element_id: The ID to search for

    Returns:
        Line number (1-indexed) or None if not found
    """
    # Search for id="elementId" or id='elementId'
    patterns = [
        f'id="{element_id}"',
        f"id='{element_id}'",
    ]

    for pattern in patterns:
        line_num = get_line_number(html_str, pattern)
        if line_num:
            return line_num

    return None


def find_modules(soup: BeautifulSoup) -> List:
    """
    Find all mktoModule elements in the template.

    Args:
        soup: BeautifulSoup object

    Returns:
        List of mktoModule elements
    """
    return soup.find_all(class_=re.compile(r'\bmktoModule\b'))


def find_variables(soup: BeautifulSoup) -> List:
    """
    Find all Marketo variable declarations in <head>.

    Args:
        soup: BeautifulSoup object

    Returns:
        List of meta tags with mkto variable classes
    """
    head = soup.find('head')
    if not head:
        return []

    # Find all meta tags with mkto variable classes
    pattern = re.compile(r'\bmkto(String|Color|Boolean|Number|List|HTML|Img)\b')
    return head.find_all('meta', class_=pattern)


def find_container(soup: BeautifulSoup) -> Optional:
    """
    Find the mktoContainer element.

    Args:
        soup: BeautifulSoup object

    Returns:
        The mktoContainer element or None
    """
    containers = soup.find_all(class_=re.compile(r'\bmktoContainer\b'))
    return containers[0] if containers else None


def find_editable_elements(soup: BeautifulSoup) -> List:
    """
    Find all editable elements (mktoText, mktoImg, mktoSnippet, mktoVideo).
    Also includes elements with 'cta' class for button elements.

    Args:
        soup: BeautifulSoup object

    Returns:
        List of editable elements
    """
    # Find mkto elements
    mkto_pattern = re.compile(r'\bmkto(Text|Img|Snippet|Video)\b')
    mkto_elements = soup.find_all(class_=mkto_pattern)

    # Find cta elements (buttons)
    cta_elements = soup.find_all(class_=re.compile(r'\bcta\b'))

    # Combine and deduplicate by element id
    seen = {}
    for elem in mkto_elements + cta_elements:
        eid = elem.get('id', id(elem))
        if eid not in seen:
            seen[eid] = elem
    return list(seen.values())


def get_element_html(element) -> str:
    """
    Convert a BeautifulSoup element to HTML string.

    Args:
        element: BeautifulSoup element

    Returns:
        HTML string representation
    """
    return str(element)


def extract_module_name(element) -> str:
    """
    Extract the mktoName attribute from an element.
    Handles both camelCase and lowercase variants.

    Args:
        element: BeautifulSoup element

    Returns:
        Module name or empty string
    """
    # Try camelCase first (preferred)
    name = element.get('mktoName')
    if name:
        return name

    # Try lowercase variant
    name = element.get('mktoname')
    if name:
        return name

    return ''


def extract_variable_type(element) -> str:
    """
    Extract the variable type from a meta tag's class attribute.

    Args:
        element: BeautifulSoup meta element

    Returns:
        Variable type (mktoString, mktoColor, etc.) or empty string
    """
    classes = element.get('class', [])
    for cls in classes:
        if cls.startswith('mkto'):
            return cls
    return ''


def is_module_scoped(element) -> bool:
    """
    Check if a variable is module-scoped.

    Args:
        element: BeautifulSoup meta element

    Returns:
        True if module-scoped, False if global
    """
    # Check camelCase variant
    scope = element.get('mktoModuleScope')
    if scope:
        return scope.lower() == 'true'

    # Check lowercase variant
    scope = element.get('mktomodulescope')
    if scope:
        return scope.lower() == 'true'

    return False


def get_all_ids(soup: BeautifulSoup) -> Dict[str, List[int]]:
    """
    Get all IDs from the template and their line numbers.

    Args:
        soup: BeautifulSoup object

    Returns:
        Dictionary mapping IDs to list of line numbers where they appear
    """
    html_str = str(soup)
    id_map = {}

    # Find all elements with id attribute
    elements = soup.find_all(id=True)

    for element in elements:
        element_id = element.get('id')
        if element_id:
            line_num = find_element_line_number(html_str, element_id)
            if line_num:
                if element_id not in id_map:
                    id_map[element_id] = []
                id_map[element_id].append(line_num)

    return id_map


def strip_styles_from_element(element):
    """
    Remove all <style> tags from an element.

    Args:
        element: BeautifulSoup element

    Returns:
        Modified element (in-place)
    """
    for style in element.find_all('style'):
        style.decompose()
    return element


def get_module_add_by_default(element) -> bool:
    """
    Check if module has mktoAddByDefault attribute.

    Marketo defaults to true when the attribute is absent.

    Args:
        element: BeautifulSoup module element

    Returns:
        The boolean value of mktoAddByDefault, defaulting to True (Marketo's default)
    """
    add_by_default = element.get('mktoAddByDefault') or element.get('mktoaddbydefault')
    if add_by_default:
        return add_by_default.lower() == 'true'
    return True


def extract_editable_element_info(element) -> dict:
    """
    Extract detailed information about an editable element.

    Args:
        element: BeautifulSoup editable element

    Returns:
        Dictionary with id, type, and name
    """
    elem_id = element.get('id', '')
    elem_classes = element.get('class', [])
    elem_name = extract_module_name(element)

    # Determine element type from classes
    elem_type = 'unknown'
    for cls in elem_classes:
        if cls.startswith('mkto'):
            elem_type = cls
            break
        elif cls == 'cta':
            elem_type = 'cta'
            break

    return {
        'id': elem_id,
        'type': elem_type,
        'name': elem_name
    }


def build_variable_lookup(soup: BeautifulSoup) -> Dict[str, dict]:
    """
    Build a lookup dict from <head> meta variable declarations.

    Maps variable id to {type, default, name} for quick lookups.

    Args:
        soup: BeautifulSoup object

    Returns:
        Dictionary mapping variable id to {type, default, name}
    """
    variables = find_variables(soup)
    lookup = {}
    for var in variables:
        var_id = var.get('id', '')
        if not var_id:
            continue
        lookup[var_id] = {
            'type': extract_variable_type(var),
            'default': var.get('default', ''),
            'name': var.get('mktoName') or var.get('mktoname', ''),
            'units': var.get('units', ''),
            'true_value': var.get('true_value', ''),
            'false_value': var.get('false_value', ''),
        }
    return lookup


def is_style_variable(var_id: str, var_info: dict) -> bool:
    """
    Determine whether a variable is a styling/layout variable (True) or a
    content variable that typically needs to be set per-email (False).

    Style variables include colors, padding, font sizes, border radii,
    boolean toggles, and layout utility lists. Content variables are things
    like URLs, link targets, and preheader text.

    Args:
        var_id: The variable id (e.g. "pad_top16", "bg_image_url")
        var_info: Dict with at least 'type' key from build_variable_lookup

    Returns:
        True if the variable is a styling/layout default, False if content
    """
    vtype = var_info.get('type', '')

    # Colors, booleans, and numbers are always styling
    if vtype in ('mktoColor', 'mktoBoolean', 'mktoNumber'):
        return True

    # mktoList variables (clr, lcr, font_fallback) are layout utilities
    if vtype == 'mktoList':
        return True

    # mktoString: check by naming convention
    # URL, link, and preheader variables are content
    return False
