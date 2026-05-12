#!/usr/bin/env bash
# check-delegates.sh
# UserPromptSubmit hook: inject completed delegate notifications before each user message.
# If the inbox has entries, they appear as context at the top of the next response.

INBOX="$CLAUDE_PROJECT_DIR/.claude/tmp/delegates/inbox.md"

[ -f "$INBOX" ] || exit 0

content=$(cat "$INBOX")
[ -z "${content// }" ] && exit 0

echo "=== DELEGATE NOTIFICATIONS (completed since last message) ==="
echo "$content"
echo "=== END DELEGATE NOTIFICATIONS ==="

# Clear inbox after surfacing
> "$INBOX"

exit 0
