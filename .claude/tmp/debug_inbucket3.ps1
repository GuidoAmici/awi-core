$msgs = Invoke-RestMethod -Uri "http://localhost:54324/api/v1/messages"
Write-Host "Total messages: $($msgs.total)"
$msgs.messages | ForEach-Object {
    Write-Host "ID: $($_.ID) | To: $($_.To) | Subject: $($_.Subject)"
}
if ($msgs.messages.Count -gt 0) {
    $id = $msgs.messages[0].ID
    Write-Host ""
    Write-Host "Fetching message $id"
    $msg = Invoke-RestMethod -Uri "http://localhost:54324/api/v1/messages/$id"
    Write-Host "Body text: $($msg.Text)"
}
