$ts = [int](Get-Date -UFormat %s)
$adminEmail = "admin$ts@newhaze.ar"
$adminPass = "Test1234!"
$body = '{"email":"' + $adminEmail + '","password":"' + $adminPass + '","role":"consumer"}'
Write-Host "Registering: $adminEmail"
Write-Host "Body: $body"
try {
    $r = Invoke-RestMethod -Uri 'http://localhost:5109/api/auth/register' -Method POST -ContentType 'application/json' -Body $body -ErrorAction Stop
    Write-Host "Success: $($r | ConvertTo-Json)"
} catch {
    $resp = $_.Exception.Response
    $stream = $resp.GetResponseStream()
    $reader = New-Object System.IO.StreamReader($stream)
    Write-Host "Failed ($($resp.StatusCode.value__)): $($reader.ReadToEnd())"
}
