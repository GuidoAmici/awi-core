#!/bin/bash
# Auto-commit vault changes after Write/Edit/Bash(mv) operations

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_name',''))" 2>/dev/null)
FILE_PATH=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path') or d.get('tool_input',{}).get('filePath') or '')" 2>/dev/null)
COMMAND=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('command',''))" 2>/dev/null)

# Handle Bash tool: only act on mv / git mv commands
if [ "$TOOL_NAME" = "Bash" ]; then
  if echo "$COMMAND" | grep -qE '(^|[;&|[:space:]])(git[[:space:]]+mv|mv)[[:space:]]'; then
    cd "$CLAUDE_PROJECT_DIR" || exit 0
    if ! git diff --cached --quiet 2>/dev/null; then
      SUMMARY=$(git diff --cached --name-status | awk '{print $NF}' | xargs -I{} basename {} | paste -sd ', ')
      git commit -m "cos: move/rename - $SUMMARY"
    fi
  fi
  exit 0
fi

[ -z "$FILE_PATH" ] && exit 0

VAULT_ROOT="$CLAUDE_PROJECT_DIR"
REL_PATH="${FILE_PATH#$VAULT_ROOT/}"

# Skip gitignored files
git check-ignore -q "$FILE_PATH" 2>/dev/null && exit 0

# Derive type from path
# Structure: _documentation/_agenda/<type>/  or  _documentation/_context/  or  system/  or  users/
IFS='/' read -ra PARTS <<< "$REL_PATH"
if [ "${PARTS[0]}" = "_documentation" ]; then
  LAYER="${PARTS[1]}"   # _agenda, _context, ...
  SUBFOLDER="${PARTS[2]}" # tasks, projects, people, ...
  if [ "$LAYER" = "_agenda" ]; then
    case "$SUBFOLDER" in
      tasks) TYPE="task" ;;
      projects) TYPE="project" ;;
      people) TYPE="person" ;;
      ideas) TYPE="idea" ;;
      daily) TYPE="daily plan" ;;
      weekly) TYPE="weekly summary" ;;
      outputs) TYPE="output" ;;
      products) TYPE="product" ;;
      planning) TYPE="planning" ;;
      user-profile-inference) TYPE="user-profile-inference" ;;
      *) TYPE="${SUBFOLDER:-_agenda}" ;;
    esac
  elif [ "$LAYER" = "_context" ]; then
    TYPE="context"
  else
    TYPE="${LAYER:-_documentation}"
  fi
elif [ "${PARTS[0]}" = "system" ]; then
  TYPE="system"
elif [ "${PARTS[0]}" = "users" ]; then
  TYPE="user"
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

# Mirror to public repo if file is on the whitelist.
# Requires .claude/config/public-repo-path to be set — exits silently if not configured.
bash "$VAULT_ROOT/.claude/hooks/sync-public.sh" "$FILE_PATH" 2>/dev/null || true

exit 0
