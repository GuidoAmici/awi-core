# check-delegates.ps1
# UserPromptSubmit hook: inject completed delegate notifications before each user message.
# If the inbox has entries, they appear as context at the top of the next response.

$InboxFile = "$env:CLAUDE_PROJECT_DIR/.claude/tmp/delegates/inbox.md"

if (-not (Test-Path $InboxFile)) { exit 0 }

$content = Get-Content $InboxFile -Raw -ErrorAction SilentlyContinue
if (-not $content -or -not $content.Trim()) { exit 0 }

# Output to stdout — UserPromptSubmit hook output is injected as context
Write-Output "=== DELEGATE NOTIFICATIONS (completed since last message) ==="
Write-Output $content.Trim()
Write-Output "=== END DELEGATE NOTIFICATIONS ==="

# Clear inbox after surfacing
Set-Content $InboxFile "" -ErrorAction SilentlyContinue

exit 0
