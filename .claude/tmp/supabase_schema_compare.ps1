$token = (& powershell -Command "[System.Environment]::GetEnvironmentVariable('SUPABASE_PERSONAL_TOKEN','User')")
$headers = @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" }

function Invoke-Sql($project, $sql) {
    $body = @{ query = $sql } | ConvertTo-Json
    try {
        Invoke-RestMethod -Uri "https://api.supabase.com/v1/projects/$project/database/query" `
            -Method POST -Headers $headers -Body $body
    } catch {
        Write-Host "ERROR: $($_.ErrorDetails.Message)"
        return $null
    }
}

$prod = "rbszzkivswvqagasrvdj"
$beta = "rpgoixcgwynerezrxqhx"

$schemaQuery = @"
SELECT t.tablename,
       c.column_name,
       c.data_type,
       c.is_nullable,
       t.rowsecurity
FROM pg_tables t
JOIN information_schema.columns c ON c.table_name = t.tablename AND c.table_schema = 'public'
WHERE t.schemaname = 'public'
ORDER BY t.tablename, c.ordinal_position
"@

Write-Host "=== PROD ==="
$prodSchema = Invoke-Sql $prod $schemaQuery
$prodSchema | ConvertTo-Json -Depth 5

Write-Host ""
Write-Host "=== BETA ==="
$betaSchema = Invoke-Sql $beta $schemaQuery
$betaSchema | ConvertTo-Json -Depth 5
