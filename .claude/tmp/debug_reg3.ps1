$ts = [int](Get-Date -UFormat %s)
$email = "admin$ts@newhaze.ar"
Write-Host "Registering: $email"
try {
    $r = Invoke-RestMethod -Uri 'http://localhost:5109/api/auth/register' -Method POST -ContentType 'application/json' -Body "{`"email`":`"$email`",`"password`":`"Test1234!`",`"role`":`"consumer`"}" -ErrorAction Stop
    Write-Host "Success: $($r | ConvertTo-Json)"
} catch {
    $resp = $_.Exception.Response
    $stream = $resp.GetResponseStream()
    $reader = New-Object System.IO.StreamReader($stream)
    Write-Host "Failed ($($resp.StatusCode.value__)): $($reader.ReadToEnd())"
}
