$paths = @('/api/v1/mailbox', '/api/v2/mailbox', '/mailbox', '/api/v1/monitor/messages', '/api/v1/messages')
foreach ($p in $paths) {
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:54324$p" -UseBasicParsing -ErrorAction Stop
        Write-Host "$p -> $($r.StatusCode): $($r.Content.Substring(0, 120))"
    } catch {
        Write-Host "$p -> ERROR: $($_.Exception.Message)"
    }
}
