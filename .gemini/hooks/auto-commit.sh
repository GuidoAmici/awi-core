#!/bin/bash
# Gemini-specific auto-commit for AWI
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Gemini AfterTool hook doesn't pass tool input via stdin in the same way,
# so we check what changed in the git index.
cd "$VAULT_ROOT" || exit 0

# Get changed files in _data/entities/ or _system/
CHANGED_FILES=$(git diff --name-only HEAD)

for FILE_PATH in $CHANGED_FILES; do
  # Skip if not in vault areas
  [[ "$FILE_PATH" != _data/entities/* && "$FILE_PATH" != _system/* ]] && continue
  
  # Skip gitignored
  git check-ignore -q "$FILE_PATH" 2>/dev/null && continue

  # Derive type (simplified logic from Claude version)
  IFS='/' read -ra PARTS <<< "$FILE_PATH"
  if [ "${PARTS[0]}" = "_data" ]; then
    TYPE="${PARTS[3]:-data}"
  elif [ "${PARTS[0]}" = "_system" ]; then
    TYPE="system"
  else
    TYPE="core"
  fi
  
  FILENAME=$(basename "$FILE_PATH" .md)
  
  git add "$FILE_PATH"
  git commit -m "cos: gemini update $TYPE - $FILENAME" 2>/dev/null
done

# Optional: Sound on success
bash "$SCRIPT_DIR/victory-sound.sh" 2>/dev/null
