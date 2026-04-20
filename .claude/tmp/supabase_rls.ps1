$token = (& powershell -Command "[System.Environment]::GetEnvironmentVariable('SUPABASE_PERSONAL_TOKEN','User')")
$project = "rbszzkivswvqagasrvdj"
$headers = @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" }

function Invoke-Sql($sql) {
    $body = @{ query = $sql } | ConvertTo-Json
    try {
        $r = Invoke-RestMethod -Uri "https://api.supabase.com/v1/projects/$project/database/query" `
            -Method POST -Headers $headers -Body $body
        return $r
    } catch {
        Write-Host "ERROR: $($_.ErrorDetails.Message)"
        return $null
    }
}

Write-Host "=== user_emails columns ==="
Invoke-Sql "SELECT column_name FROM information_schema.columns WHERE table_name = 'user_emails' ORDER BY ordinal_position" | ConvertTo-Json

Write-Host "=== waitlist columns ==="
Invoke-Sql "SELECT column_name FROM information_schema.columns WHERE table_name = 'waitlist' ORDER BY ordinal_position" | ConvertTo-Json

Write-Host "=== existing policies ==="
Invoke-Sql "SELECT tablename, policyname FROM pg_policies WHERE tablename IN ('user_emails','waitlist')" | ConvertTo-Json
