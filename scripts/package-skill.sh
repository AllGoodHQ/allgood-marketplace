#!/bin/bash
set -euo pipefail

SKILL_DIR="${1:?Usage: ./scripts/package-skill.sh <skill-folder> [output-dir]}"
OUT_DIR="${2:-dist}"
SKILL_NAME=$(basename "$SKILL_DIR")

# Validate SKILL.md exists
if [ ! -f "$SKILL_DIR/SKILL.md" ]; then
  echo "Error: SKILL.md not found in $SKILL_DIR"
  exit 1
fi

mkdir -p "$OUT_DIR"

# Build .skill file (zip with .skill extension)
cd "$(dirname "$SKILL_DIR")"
zip -r "$OLDPWD/$OUT_DIR/$SKILL_NAME.skill" "$SKILL_NAME" \
  -x "*/.claude/*" "*/.*" "*/__pycache__/*"

echo "Packaged: $OUT_DIR/$SKILL_NAME.skill"
