#!/bin/bash
# Auto-commit vault changes after Write/Edit operations

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path') or d.get('tool_input',{}).get('filePath') or '')" 2>/dev/null)

[ -z "$FILE_PATH" ] && exit 0

VAULT_ROOT="$CLAUDE_PROJECT_DIR"
REL_PATH="${FILE_PATH#$VAULT_ROOT/}"

# Skip gitignored files
git check-ignore -q "$FILE_PATH" 2>/dev/null && exit 0

# Derive type from path
IFS='/' read -ra PARTS <<< "$REL_PATH"
SUBFOLDER="${PARTS[1]}"
if [ "${PARTS[0]}" = "_documents" ]; then
  if [ "$SUBFOLDER" = "organization" ] && [ "${#PARTS[@]}" -gt 2 ]; then
    SUBFOLDER="${PARTS[2]}"
  fi
  case "$SUBFOLDER" in
    tasks) TYPE="task" ;;
    projects) TYPE="project" ;;
    people) TYPE="person" ;;
    ideas) TYPE="idea" ;;
    daily) TYPE="daily plan" ;;
    weekly) TYPE="weekly summary" ;;
    outputs) TYPE="output" ;;
    context) TYPE="context" ;;
    products) TYPE="product" ;;
    planning) TYPE="planning" ;;
    wiki) TYPE="wiki" ;;
    user-profile-inference) TYPE="user-profile-inference" ;;
    *) TYPE="$SUBFOLDER" ;;
  esac
else
  TYPE="${PARTS[0]}"
fi

FILENAME=$(basename "$FILE_PATH" .md)

cd "$VAULT_ROOT" || exit 0

if git diff --quiet "$FILE_PATH" 2>/dev/null && git diff --cached --quiet "$FILE_PATH" 2>/dev/null; then
  if ! git ls-files --error-unmatch "$FILE_PATH" 2>/dev/null; then
    git add "$FILE_PATH"
    git commit -m "cos: new $TYPE - $FILENAME"
  fi
else
  git add "$FILE_PATH"
  git commit -m "cos: update $TYPE - $FILENAME"
fi

exit 0
