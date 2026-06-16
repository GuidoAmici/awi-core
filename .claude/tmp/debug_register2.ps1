try {
    $r = Invoke-RestMethod -Uri 'http://localhost:5109/api/auth/register' -Method POST -ContentType 'application/json' -Body '{"email":"guido@newhaze.ar","password":"321654","role":"consumer"}' -ErrorAction Stop
    Write-Host "Register success: $($r | ConvertTo-Json)"
} catch {
    $resp = $_.Exception.Response
    $stream = $resp.GetResponseStream()
    $reader = New-Object System.IO.StreamReader($stream)
    $body = $reader.ReadToEnd()
    Write-Host "Register failed ($($resp.StatusCode.value__)): $body"
}
