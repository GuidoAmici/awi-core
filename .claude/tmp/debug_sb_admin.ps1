$sbUrl = "http://localhost:54321"
$sbKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hj04zWl196z2-SB38"
$adminEmail = "guido@newhaze.ar"

Write-Host "1. Listing users..."
try {
    $r = Invoke-RestMethod -Uri "$sbUrl/auth/v1/admin/users" -Method GET -Headers @{ apikey = $sbKey; Authorization = "Bearer $sbKey" }
    Write-Host "Users found: $($r.users.Count)"
    $r.users | ForEach-Object { Write-Host "  $($_.id) | $($_.email) | confirmed: $($_.email_confirmed_at)" }
} catch {
    $resp = $_.Exception.Response
    $stream = $resp.GetResponseStream()
    $reader = New-Object System.IO.StreamReader($stream)
    Write-Host "Error ($($resp.StatusCode.value__)): $($reader.ReadToEnd())"
}
