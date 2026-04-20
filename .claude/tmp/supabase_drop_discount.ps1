$token = (& powershell -Command "[System.Environment]::GetEnvironmentVariable('SUPABASE_PERSONAL_TOKEN','User')")
$headers = @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" }
$beta = "rpgoixcgwynerezrxqhx"

$body = @{ query = "ALTER TABLE profiles DROP COLUMN IF EXISTS discount_rate" } | ConvertTo-Json -Compress
Invoke-RestMethod -Uri "https://api.supabase.com/v1/projects/$beta/database/query" -Method POST -Headers $headers -Body $body | Out-Null
Write-Host "OK: dropped discount_rate"

$body = @{ query = "SELECT column_name FROM information_schema.columns WHERE table_name = 'profiles' AND table_schema = 'public' ORDER BY ordinal_position" } | ConvertTo-Json -Compress
Write-Host "BETA profiles columns:"
(Invoke-RestMethod -Uri "https://api.supabase.com/v1/projects/$beta/database/query" -Method POST -Headers $headers -Body $body) | ForEach-Object { Write-Host "  $($_.column_name)" }
