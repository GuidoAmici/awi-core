$base = "http://localhost:5109"
$inbucket = "http://localhost:54324"
$errors = @()
$passed = @()

function Pass($msg) { Write-Host "PASS $msg" -ForegroundColor Green; $script:passed += $msg }
function Fail($msg) { Write-Host "FAIL $msg" -ForegroundColor Red; $script:errors += $msg }
function Info($msg) { Write-Host "     $msg" -ForegroundColor Gray }

function Get-OTP($email) {
    $deadline = (Get-Date).AddSeconds(15)
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Seconds 2
        try {
            $msgs = Invoke-RestMethod -Uri "$inbucket/api/v1/messages"
            $match = $msgs.messages | Where-Object { $_.To[0].Address -eq $email } | Sort-Object Created -Descending | Select-Object -First 1
            if ($match) {
                $otp = [regex]::Match($match.Snippet, '\b(\d{6})\b').Groups[1].Value
                if ($otp) { return $otp }
            }
        } catch {}
    }
    return $null
}

$ts = [int](Get-Date -UFormat %s)

# ── [1] Bootstrap admin using unique @newhaze.ar address ─────────────────────
Write-Host "[1] Bootstrap admin" -ForegroundColor Cyan
$adminEmail = "admin$ts@newhaze.ar"
$adminPass = "Test1234!"
try {
    $body = '{"email":"' + $adminEmail + '","password":"' + $adminPass + '","role":"consumer"}'
    Invoke-RestMethod -Uri "$base/api/auth/register" -Method POST -ContentType 'application/json' -Body $body | Out-Null
    $otp = Get-OTP $adminEmail
    if (-not $otp) { Fail "No OTP for admin in Inbucket"; exit }
    $body2 = '{"email":"' + $adminEmail + '","token":"' + $otp + '"}'
    $adminSession = Invoke-RestMethod -Uri "$base/api/auth/verify-otp" -Method POST -ContentType 'application/json' -Body $body2
    # Refresh immediately so the JWT contains the roles SyncUserMetaAsync just wrote
    $refreshed = Invoke-RestMethod -Uri "$base/api/auth/refresh" -Method POST -ContentType 'application/json' -Body ('{"refreshToken":"' + $adminSession.refreshToken + '"}')
    $adminToken = $refreshed.accessToken
    Pass "Admin verified: $adminEmail"
    Info "Roles: $($adminSession.user.roles -join ', ')"
    if ($adminSession.user.roles -contains "newhaze_employee") { Pass "@newhaze.ar auto-assigned newhaze_employee" }
    else { Fail "newhaze_employee NOT auto-assigned to @newhaze.ar" }
    if ($adminSession.user.roles -contains "beta_tester") { Pass "@newhaze.ar auto-assigned beta_tester" }
    else { Fail "beta_tester NOT auto-assigned to @newhaze.ar" }
} catch {
    Fail "Admin bootstrap failed: $_"; exit
}

# ── [2] Register test user ─────────────────────────────────────────────────────
Write-Host "[2] Register test user" -ForegroundColor Cyan
$testEmail = "ssotest$ts@example.com"
$testPass = "Test1234!"
try {
    $body = '{"email":"' + $testEmail + '","password":"' + $testPass + '","role":"consumer"}'
    $reg = Invoke-RestMethod -Uri "$base/api/auth/register" -Method POST -ContentType 'application/json' -Body $body
    if ($reg.success) { Pass "Register $testEmail" }
    else { Fail "Register returned success=false" }
} catch {
    Fail "Register failed: $_"; exit
}

# ── [3] Verify OTP ─────────────────────────────────────────────────────────────
Write-Host "[3] Verify OTP" -ForegroundColor Cyan
try {
    $otp = Get-OTP $testEmail
    if ($otp) { Pass "Got OTP: $otp" }
    else { Fail "No OTP found in Inbucket"; exit }
    $body = '{"email":"' + $testEmail + '","token":"' + $otp + '"}'
    $session = Invoke-RestMethod -Uri "$base/api/auth/verify-otp" -Method POST -ContentType 'application/json' -Body $body
    $userToken = $session.accessToken
    $refreshToken = $session.refreshToken
    $userId = $session.user.id
    Pass "OTP verified, userId: $userId"
    Info "Roles: $($session.user.roles -join ', ')"
    if ($session.user.roles -contains "consumer") { Pass "Role consumer auto-assigned" }
    else { Fail "Role consumer missing" }
} catch {
    Fail "OTP flow failed: $_"; exit
}

# ── [4] GET /users/me ──────────────────────────────────────────────────────────
Write-Host "[4] GET /users/me" -ForegroundColor Cyan
try {
    $me = Invoke-RestMethod -Uri "$base/api/users/me" -Method GET -Headers @{ Authorization = "Bearer $userToken" }
    if ($me.id -eq $userId) { Pass "/users/me correct profile" }
    else { Fail "/users/me returned wrong userId" }
    Info "Username: $($me.username) | Roles: $($me.roles -join ', ')"
} catch {
    Fail "/users/me failed: $_"
}

# ── [5] Add role ───────────────────────────────────────────────────────────────
Write-Host "[5] Add role beta_tester" -ForegroundColor Cyan
try {
    $addRole = Invoke-RestMethod -Uri "$base/api/users/$userId/roles" -Method POST -ContentType 'application/json' -Headers @{ Authorization = "Bearer $adminToken" } -Body '{"role":"beta_tester"}'
    if ($addRole.roles -contains "beta_tester") { Pass "Role beta_tester added" }
    else { Fail "beta_tester not in roles: $($addRole.roles -join ', ')" }
} catch {
    Fail "Add role failed: $_"
}

# ── [6] Refresh + decode JWT ───────────────────────────────────────────────────
Write-Host "[6] Refresh + JWT decode" -ForegroundColor Cyan
try {
    $body = '{"refreshToken":"' + $refreshToken + '"}'
    $refreshed = Invoke-RestMethod -Uri "$base/api/auth/refresh" -Method POST -ContentType 'application/json' -Body $body
    $parts = $refreshed.accessToken -split '\.'
    $pad = $parts[1].Length % 4
    $padded = if ($pad -eq 0) { $parts[1] } else { $parts[1].PadRight($parts[1].Length + (4 - $pad), '=') }
    $claims = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($padded)) | ConvertFrom-Json
    $jwtRoles = $claims.user_metadata.roles
    Info "JWT roles after refresh: $($jwtRoles -join ', ')"
    if ($jwtRoles -contains "beta_tester") { Pass "JWT contains beta_tester after refresh (SyncUserMetaAsync working)" }
    else { Fail "JWT missing beta_tester after refresh (SyncUserMetaAsync not syncing)" }
} catch {
    Fail "Refresh/JWT decode failed: $_"
}

# ── [7] Remove role ────────────────────────────────────────────────────────────
Write-Host "[7] Remove role beta_tester" -ForegroundColor Cyan
try {
    $removed = Invoke-RestMethod -Uri "$base/api/users/$userId/roles/beta_tester" -Method DELETE -Headers @{ Authorization = "Bearer $adminToken" }
    if (-not ($removed.roles -contains "beta_tester")) { Pass "Role beta_tester removed" }
    else { Fail "beta_tester still in roles after delete" }
} catch {
    Fail "Remove role failed: $_"
}

# ── [8] Negative: invalid token -> 401 ────────────────────────────────────────
Write-Host "[8] Invalid token -> 401" -ForegroundColor Cyan
try {
    Invoke-RestMethod -Uri "$base/api/users/me" -Method GET -Headers @{ Authorization = "Bearer invalidtoken" } -ErrorAction Stop
    Fail "Expected 401 but got success"
} catch {
    $code = $_.Exception.Response.StatusCode.value__
    if ($code -eq 401) { Pass "Invalid token -> 401" }
    else { Fail "Wrong status: $code" }
}

# ── [9] Negative: non-admin role call -> 403 ──────────────────────────────────
Write-Host "[9] Non-admin role call -> 403" -ForegroundColor Cyan
try {
    Invoke-RestMethod -Uri "$base/api/users/$userId/roles" -Method POST -ContentType 'application/json' -Headers @{ Authorization = "Bearer $userToken" } -Body '{"role":"beta_tester"}' -ErrorAction Stop
    Fail "Expected 403 but got success"
} catch {
    $code = $_.Exception.Response.StatusCode.value__
    if ($code -eq 403) { Pass "Non-admin role call -> 403" }
    else { Fail "Wrong status: $code" }
}

# ── Summary ────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "PASSED: $($passed.Count)  FAILED: $($errors.Count)" -ForegroundColor $(if ($errors.Count -eq 0) { 'Green' } else { 'Yellow' })
if ($errors.Count -gt 0) {
    $errors | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
}
