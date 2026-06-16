try {
    $r = Invoke-RestMethod -Uri 'http://localhost:5109/api/auth/verify-otp' -Method POST -ContentType 'application/json' -Body '{"email":"guido@newhaze.ar","token":"406238"}' -ErrorAction Stop
    Write-Host "Success: $($r | ConvertTo-Json -Depth 5)"
} catch {
    $resp = $_.Exception.Response
    $stream = $resp.GetResponseStream()
    $reader = New-Object System.IO.StreamReader($stream)
    $body = $reader.ReadToEnd()
    Write-Host "Failed ($($resp.StatusCode.value__)): $body"
}
