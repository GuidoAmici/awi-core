$token = (& powershell -Command "[System.Environment]::GetEnvironmentVariable('SUPABASE_PERSONAL_TOKEN','User')")
$project = "rbszzkivswvqagasrvdj"
$headers = @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" }

function Invoke-Sql($sql) {
    $body = @{ query = $sql } | ConvertTo-Json
    try {
        Invoke-RestMethod -Uri "https://api.supabase.com/v1/projects/$project/database/query" `
            -Method POST -Headers $headers -Body $body
    } catch {
        Write-Host "ERROR: $($_.ErrorDetails.Message)"
    }
}

# Find user_emails in any schema
Write-Host "=== user_emails location ==="
Invoke-Sql "SELECT table_schema, table_name, column_name FROM information_schema.columns WHERE table_name LIKE '%email%' ORDER BY table_schema, table_name, ordinal_position" | ConvertTo-Json

# All public tables
Write-Host "=== all public tables ==="
Invoke-Sql "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename" | ConvertTo-Json
