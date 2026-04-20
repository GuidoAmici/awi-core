$token = (& powershell -Command "[System.Environment]::GetEnvironmentVariable('SUPABASE_PERSONAL_TOKEN','User')")
$headers = @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" }

function Invoke-Sql($project, $label, $sql) {
    $body = @{ query = $sql } | ConvertTo-Json -Compress
    try {
        Invoke-RestMethod -Uri "https://api.supabase.com/v1/projects/$project/database/query" `
            -Method POST -Headers $headers -Body $body | Out-Null
        Write-Host "  OK: $label"
    } catch {
        Write-Host "  ERROR ($label): $($_.ErrorDetails.Message)"
    }
}

$beta = "rpgoixcgwynerezrxqhx"

Write-Host "=== BETA: drop redundant profiles columns ==="
Invoke-Sql $beta "drop tech_support_access" "ALTER TABLE profiles DROP COLUMN IF EXISTS tech_support_access"
Invoke-Sql $beta "drop rabbittotem_access"  "ALTER TABLE profiles DROP COLUMN IF EXISTS rabbittotem_access"
Invoke-Sql $beta "drop beta_access"         "ALTER TABLE profiles DROP COLUMN IF EXISTS beta_access"

Write-Host ""
Write-Host "=== Verify BETA profiles columns ==="
$body = @{ query = "SELECT column_name FROM information_schema.columns WHERE table_name = 'profiles' AND table_schema = 'public' ORDER BY ordinal_position" } | ConvertTo-Json -Compress
(Invoke-RestMethod -Uri "https://api.supabase.com/v1/projects/$beta/database/query" -Method POST -Headers $headers -Body $body) | ForEach-Object { Write-Host "  $($_.column_name)" }
