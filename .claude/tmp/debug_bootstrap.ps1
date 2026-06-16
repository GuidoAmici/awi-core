$base = "http://localhost:5109"
$inbucket = "http://localhost:54324"
$ts = [int](Get-Date -UFormat %s)
$adminEmail = "admin$ts@newhaze.ar"
$adminPass = "Test1234!"

Write-Host "Step 1: Register $adminEmail"
try {
    $body = '{"email":"' + $adminEmail + '","password":"' + $adminPass + '","role":"consumer"}'
    $r = Invoke-RestMethod -Uri "$base/api/auth/register" -Method POST -ContentType 'application/json' -Body $body -ErrorAction Stop
    Write-Host "Register: $($r | ConvertTo-Json)"
} catch {
    $resp = $_.Exception.Response
    $stream = $resp.GetResponseStream()
    $reader = New-Object System.IO.StreamReader($stream)
    Write-Host "Register FAILED ($($resp.StatusCode.value__)): $($reader.ReadToEnd())"
    exit
}

Write-Host "Step 2: Wait for OTP in Inbucket"
$deadline = (Get-Date).AddSeconds(15)
$otp = $null
while ((Get-Date) -lt $deadline) {
    Start-Sleep -Seconds 2
    $msgs = Invoke-RestMethod -Uri "$inbucket/api/v1/messages"
    Write-Host "Messages in Inbucket: $($msgs.total)"
    $match = $msgs.messages | Where-Object { $_.To[0].Address -eq $adminEmail } | Sort-Object Created -Descending | Select-Object -First 1
    if ($match) {
        $otp = [regex]::Match($match.Snippet, '\b(\d{6})\b').Groups[1].Value
        Write-Host "Found OTP: $otp from snippet: $($match.Snippet)"
        break
    } else {
        Write-Host "No message yet for $adminEmail"
    }
}
if (-not $otp) { Write-Host "TIMEOUT: no OTP found"; exit }

Write-Host "Step 3: Verify OTP $otp"
try {
    $body2 = '{"email":"' + $adminEmail + '","token":"' + $otp + '"}'
    $session = Invoke-RestMethod -Uri "$base/api/auth/verify-otp" -Method POST -ContentType 'application/json' -Body $body2 -ErrorAction Stop
    Write-Host "Session: $($session | ConvertTo-Json -Depth 5)"
} catch {
    $resp = $_.Exception.Response
    $stream = $resp.GetResponseStream()
    $reader = New-Object System.IO.StreamReader($stream)
    Write-Host "Verify FAILED ($($resp.StatusCode.value__)): $($reader.ReadToEnd())"
}
