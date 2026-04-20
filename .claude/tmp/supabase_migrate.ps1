$token = (& powershell -Command "[System.Environment]::GetEnvironmentVariable('SUPABASE_PERSONAL_TOKEN','User')")
$headers = @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" }

function Invoke-Sql($project, $label, $sql) {
    $body = @{ query = $sql } | ConvertTo-Json
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

# ── PROD migrations ───────────────────────────────────────────────────────────
Write-Host "=== PROD migrations ==="

Invoke-Sql $prod "profiles.email column" @"
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS email text;
"@

Invoke-Sql $prod "profiles.theme_preference column" @"
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS theme_preference text;
"@

Invoke-Sql $prod "blog_posts table" @"
CREATE TABLE IF NOT EXISTS blog_posts (
    id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    title        text NOT NULL,
    excerpt      text NOT NULL,
    cover_image  text NOT NULL,
    slug         text NOT NULL UNIQUE,
    content      text NOT NULL,
    author       text NOT NULL,
    published_at timestamptz NOT NULL,
    created_at   timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE blog_posts ENABLE ROW LEVEL SECURITY;
CREATE POLICY IF NOT EXISTS "public read" ON blog_posts FOR SELECT USING (true);
"@

# ── BETA migrations ───────────────────────────────────────────────────────────
Write-Host ""
Write-Host "=== BETA migrations ==="

Invoke-Sql $beta "waitlist table" @"
CREATE TABLE IF NOT EXISTS waitlist (
    email      text NOT NULL,
    created_at timestamptz DEFAULT now()
);
ALTER TABLE waitlist ENABLE ROW LEVEL SECURITY;
CREATE POLICY IF NOT EXISTS "allow insert" ON waitlist FOR INSERT WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "no select" ON waitlist FOR SELECT USING (false);
"@

# ── Verify ────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "=== Verify PROD profiles columns ==="
Invoke-Sql $prod "check" "SELECT column_name FROM information_schema.columns WHERE table_name = 'profiles' ORDER BY ordinal_position" | Out-Null

$verifyQuery = "SELECT column_name FROM information_schema.columns WHERE table_name = 'profiles' ORDER BY ordinal_position"
$body = @{ query = $verifyQuery } | ConvertTo-Json
$r = Invoke-RestMethod -Uri "https://api.supabase.com/v1/projects/$prod/database/query" -Method POST -Headers $headers -Body $body
$r | ForEach-Object { Write-Host "  $($_.column_name)" }

Write-Host ""
Write-Host "=== Verify PROD tables ==="
$body = @{ query = "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename" } | ConvertTo-Json
$r = Invoke-RestMethod -Uri "https://api.supabase.com/v1/projects/$prod/database/query" -Method POST -Headers $headers -Body $body
$r | ForEach-Object { Write-Host "  $($_.tablename)" }

Write-Host ""
Write-Host "=== Verify BETA tables ==="
$body = @{ query = "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename" } | ConvertTo-Json
$r = Invoke-RestMethod -Uri "https://api.supabase.com/v1/projects/$beta/database/query" -Method POST -Headers $headers -Body $body
$r | ForEach-Object { Write-Host "  $($_.tablename)" }
