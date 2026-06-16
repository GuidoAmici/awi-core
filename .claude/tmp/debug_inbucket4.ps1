$msgs = Invoke-RestMethod -Uri "http://localhost:54324/api/v1/messages"
$msg = $msgs.messages[0]
Write-Host "Full message object:"
$msg | ConvertTo-Json -Depth 5

# Try different body endpoints
$id = $msg.ID
$paths = @(
    "/api/v1/messages/$id/body",
    "/api/v1/message/$id",
    "/api/v1/messages/$id/source"
)
foreach ($p in $paths) {
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:54324$p" -UseBasicParsing -ErrorAction Stop
        Write-Host "$p -> 200: $($r.Content.Substring(0, 200))"
    } catch {
        Write-Host "$p -> ERROR: $($_.Exception.Message)"
    }
}
