$token = (& powershell -Command "[System.Environment]::GetEnvironmentVariable('SUPABASE_PERSONAL_TOKEN','User')")
$project = "rbszzkivswvqagasrvdj"
$headers = @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" }

function Invoke-Sql($label, $sql) {
    Write-Host "=== $label ==="
    $body = @{ query = $sql } | ConvertTo-Json
    try {
        $r = Invoke-RestMethod -Uri "https://api.supabase.com/v1/projects/$project/database/query" `
            -Method POST -Headers $headers -Body $body
        Write-Host "OK"
        $r | ConvertTo-Json
    } catch {
        Write-Host "ERROR: $($_.ErrorDetails.Message)"
    }
}

Invoke-Sql "Enable RLS on waitlist" "ALTER TABLE waitlist ENABLE ROW LEVEL SECURITY"

Invoke-Sql "waitlist: allow INSERT for anyone" @"
CREATE POLICY "allow insert"
ON waitlist
FOR INSERT
WITH CHECK (true)
"@

Invoke-Sql "waitlist: block SELECT from clients" @"
CREATE POLICY "no select"
ON waitlist
FOR SELECT
USING (false)
"@

Invoke-Sql "Verify policies" "SELECT tablename, policyname, cmd FROM pg_policies WHERE tablename = 'waitlist'"
