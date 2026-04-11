#!/bin/bash
# Mirror a file to the public (forkable) repo if it matches the whitelist.
# Called by auto-commit.sh after each successful private commit.
# Usage: sync-public.sh <absolute-file-path>

FILE_PATH="$1"
VAULT_ROOT="$CLAUDE_PROJECT_DIR"
CONFIG_DIR="$VAULT_ROOT/.claude/config"
WHITELIST="$CONFIG_DIR/public-whitelist"
PATH_FILE="$CONFIG_DIR/public-repo-path"

# Exit silently if public sync is not configured
[ -f "$PATH_FILE" ] || exit 0
[ -f "$WHITELIST" ]  || exit 0
[ -n "$FILE_PATH" ]  || exit 0

PUBLIC_REPO=$(tr -d '[:space:]' < "$PATH_FILE")
[ -d "$PUBLIC_REPO/.git" ] || exit 0

REL_PATH="${FILE_PATH#$VAULT_ROOT/}"

# Resolve sync decision:
#   1. Path whitelist — folder/file structural defaults
#   2. kind: workflow in frontmatter — opt-in for individual files outside whitelisted paths
#   3. kind: context in frontmatter — opt-out for individual files inside whitelisted paths

# Read kind field from markdown frontmatter (empty string if not present or not .md)
KIND=""
if [[ "$FILE_PATH" == *.md ]]; then
  KIND=$(awk '/^---/{if(found) exit; found=1; next} found && /^kind:/{print $2; exit}' "$FILE_PATH" 2>/dev/null)
fi

# Explicit opt-out overrides everything
[[ "$KIND" == "context" ]] && exit 0

# Check path whitelist
IN_WHITELIST=false
while IFS= read -r pattern; do
  [[ -z "$pattern" || "$pattern" == \#* ]] && continue
  if [[ "$REL_PATH" == "$pattern" || "$REL_PATH" == "$pattern/"* ]]; then
    IN_WHITELIST=true
    break
  fi
done < "$WHITELIST"

# Sync if in whitelist OR explicitly tagged workflow
[[ "$IN_WHITELIST" == true || "$KIND" == "workflow" ]] || exit 0

# Determine if this is a new file in the public repo (before mirroring)
cd "$PUBLIC_REPO" || exit 0
IS_NEW=true
git ls-files --error-unmatch "$REL_PATH" 2>/dev/null && IS_NEW=false

# Mirror file
DEST="$PUBLIC_REPO/$REL_PATH"
mkdir -p "$(dirname "$DEST")"
cp "$FILE_PATH" "$DEST"

# Commit
git add "$REL_PATH"
git diff --cached --quiet && exit 0

FILENAME=$(basename "$REL_PATH" .md)
FOLDER=$(basename "$(dirname "$REL_PATH")")
if $IS_NEW; then
  git commit -m "cos: new $FOLDER - $FILENAME"
else
  git commit -m "cos: update $FOLDER - $FILENAME"
fi

exit 0
