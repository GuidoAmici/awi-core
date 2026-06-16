$mailbox = "guido"
Write-Host "Fetching mailbox: $mailbox"
try {
    $msgs = Invoke-RestMethod -Uri "http://localhost:54324/api/v1/mailbox/$mailbox"
    Write-Host "Messages: $($msgs | ConvertTo-Json -Depth 3)"
    if ($msgs.Count -gt 0) {
        $msgId = $msgs[0].id
        Write-Host "Fetching message: $msgId"
        $msg = Invoke-RestMethod -Uri "http://localhost:54324/api/v1/mailbox/$mailbox/$msgId"
        Write-Host "Body text: $($msg.body.text)"
    }
} catch {
    Write-Host "Error: $_"
    # Try listing all mailboxes
    try {
        $all = Invoke-RestMethod -Uri "http://localhost:54324/api/v1/mailbox"
        Write-Host "All mailboxes: $($all | ConvertTo-Json)"
    } catch {
        Write-Host "Can't list mailboxes: $_"
    }
}
