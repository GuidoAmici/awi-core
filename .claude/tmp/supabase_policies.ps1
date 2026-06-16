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

$prod = "rbszzkivswvqagasrvdj"
$beta = "rpgoixcgwynerezrxqhx"

Write-Host "=== PROD: blog_posts policies ==="
Invoke-Sql $prod "public read" 'CREATE POLICY "public read" ON blog_posts FOR SELECT USING (true)'
Invoke-Sql $prod "no direct write" 'CREATE POLICY "no direct write" ON blog_posts FOR INSERT USING (false) WITH CHECK (false)'

Write-Host ""
Write-Host "=== BETA: waitlist policies ==="
Invoke-Sql $beta "allow insert" 'CREATE POLICY "allow insert" ON waitlist FOR INSERT WITH CHECK (true)'
Invoke-Sql $beta "no select" 'CREATE POLICY "no select" ON waitlist FOR SELECT USING (false)'

Write-Host ""
Write-Host "=== Verify policies ==="
$q = 'SELECT tablename, policyname, cmd FROM pg_policies WHERE tablename IN (''blog_posts'',''waitlist'') ORDER BY tablename, policyname'
$body = @{ query = $q } | ConvertTo-Json -Compress
Write-Host "PROD:"
(Invoke-RestMethod -Uri "https://api.supabase.com/v1/projects/$prod/database/query" -Method POST -Headers $headers -Body $body) | ForEach-Object { Write-Host "  $($_.tablename) | $($_.policyname) | $($_.cmd)" }
Write-Host "BETA:"
(Invoke-RestMethod -Uri "https://api.supabase.com/v1/projects/$beta/database/query" -Method POST -Headers $headers -Body $body) | ForEach-Object { Write-Host "  $($_.tablename) | $($_.policyname) | $($_.cmd)" }
