#!/usr/bin/env bash
# Setup script for marketo-parser skill
# Checks dependencies and installs if needed

set -e

echo "=== Marketo Parser Skill Setup ==="
echo ""

# Check for Python 3
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo "✓ Found: $PYTHON_VERSION"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1)
    if [[ $PYTHON_VERSION == *"Python 3"* ]]; then
        PYTHON_CMD="python"
        echo "✓ Found: $PYTHON_VERSION"
    else
        echo "✗ Error: Python 3.x is required"
        echo "  Found: $PYTHON_VERSION"
        exit 1
    fi
else
    echo "✗ Error: Python 3 not found"
    echo "  Install Python 3: https://www.python.org/downloads/"
    exit 1
fi

# Check for pip
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
else
    echo "✗ Error: pip not found"
    echo "  Install pip: $PYTHON_CMD -m ensurepip"
    exit 1
fi

echo "✓ Found: pip"
echo ""

# Check for BeautifulSoup4
echo "Checking dependencies..."
if $PYTHON_CMD -c "import bs4" 2>/dev/null; then
    BS4_VERSION=$($PYTHON_CMD -c "import bs4; print(bs4.__version__)" 2>/dev/null)
    echo "✓ beautifulsoup4 $BS4_VERSION already installed"
else
    echo "Installing beautifulsoup4..."
    $PIP_CMD install beautifulsoup4
    echo "✓ beautifulsoup4 installed"
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Usage:"
echo "  python3 scripts/generate_registry.py <template.html>"
echo "  python3 scripts/list_modules.py <template.html>"
echo "  python3 scripts/validate.py <template.html>"
echo ""
