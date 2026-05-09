#!/bin/bash
# check-delegates.sh
# Get the directory where the script is located and derive vault root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$SCRIPT_DIR/../.." && pwd)}"

INBOX_FILE="$VAULT_ROOT/.claude/tmp/delegates/inbox.md"

if [ ! -f "$INBOX_FILE" ]; then exit 0; fi

CONTENT=$(cat "$INBOX_FILE" 2>/dev/null)

if [ -z "$(echo "$CONTENT" | tr -d '[:space:]')" ]; then exit 0; fi

# Output to stdout — UserPromptSubmit hook output is injected as context
echo "=== DELEGATE NOTIFICATIONS (completed since last message) ==="
echo "$CONTENT" | sed '/^[[:space:]]*$/d'
echo "=== END DELEGATE NOTIFICATIONS ==="

# Clear inbox after surfacing
> "$INBOX_FILE"

exit 0
