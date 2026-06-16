$msgs = Invoke-RestMethod -Uri "http://localhost:54324/api/v1/messages"
Write-Host "All messages ($($msgs.total) total):"
$msgs.messages | ForEach-Object {
    Write-Host "  $($_.Created) | To: $($_.To[0].Address) | OTP: $([regex]::Match($_.Snippet, '\b(\d{6})\b').Groups[1].Value) | Snippet: $($_.Snippet)"
}
