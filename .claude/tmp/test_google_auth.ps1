$body = '{"googleToken":"invalid.token.here"}'
try {
    $response = Invoke-RestMethod -Uri 'https://api.newhaze.ar/api/auth/google' -Method POST -ContentType 'application/json' -Body $body
    Write-Host "UNEXPECTED 200:"
    $response | ConvertTo-Json
} catch {
    $status = $_.Exception.Response.StatusCode.value__
    $detail = $_.ErrorDetails.Message
    Write-Host "Status: $status"
    Write-Host "Body: $detail"
}
