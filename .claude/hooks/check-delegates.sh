#!/usr/bin/env bash
# check-delegates.sh
# UserPromptSubmit hook: inject completed delegate notifications before each user message.
# If the inbox has entries, they appear as context at the top of the next response.

# Derive project root from the script's own location (.claude/hooks/ -> two levels up).
# Falls back to $CLAUDE_PROJECT_DIR if realpath resolution fails.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
if [[ -n "$SCRIPT_DIR" ]]; then
    PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." 2>/dev/null && pwd)"
fi
PROJECT_ROOT="${PROJECT_ROOT:-$CLAUDE_PROJECT_DIR}"

INBOX="$PROJECT_ROOT/.claude/tmp/delegates/inbox.md"

[ -f "$INBOX" ] || exit 0

# Atomic read-and-clear: move inbox to a temp file so concurrent delegate
# completions do not lose entries written between our read and the clear.
INBOX_TMP="${INBOX}.reading.$$"
mv "$INBOX" "$INBOX_TMP" 2>/dev/null || exit 0

content=$(cat "$INBOX_TMP" 2>/dev/null)
rm -f "$INBOX_TMP"

# Skip if content is blank (only whitespace characters)
[[ -z "${content//[[:space:]]/}" ]] && exit 0

echo "=== DELEGATE NOTIFICATIONS (completed since last message) ==="
printf '%s\n' "$content"
echo "=== END DELEGATE NOTIFICATIONS ==="

exit 0
