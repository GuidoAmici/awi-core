try {
    $r = Invoke-RestMethod -Uri 'http://localhost:5109/api/auth/login' -Method POST -ContentType 'application/json' -Body '{"email":"guido@newhaze.ar","password":"321654"}' -ErrorAction Stop
    Write-Host "Success:"
    $r | ConvertTo-Json
} catch {
    $response = $_.Exception.Response
    $stream = $response.GetResponseStream()
    $reader = New-Object System.IO.StreamReader($stream)
    $body = $reader.ReadToEnd()
    Write-Host "Status: $($response.StatusCode.value__)"
    Write-Host "Body: $body"
}
