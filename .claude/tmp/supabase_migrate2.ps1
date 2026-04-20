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

Write-Host "=== PROD: blog_posts ==="
Invoke-Sql $prod "create table" @"
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
"@

Invoke-Sql $prod "enable RLS" "ALTER TABLE blog_posts ENABLE ROW LEVEL SECURITY;"

Invoke-Sql $prod "public read policy" @"
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'public read' AND tablename = 'blog_posts') THEN
    EXECUTE 'CREATE POLICY "public read" ON blog_posts FOR SELECT USING (true)';
  END IF;
END $$;
"@

Write-Host ""
Write-Host "=== BETA: waitlist ==="
Invoke-Sql $beta "create table" @"
CREATE TABLE IF NOT EXISTS waitlist (
    email      text NOT NULL,
    created_at timestamptz DEFAULT now()
);
"@

Invoke-Sql $beta "enable RLS" "ALTER TABLE waitlist ENABLE ROW LEVEL SECURITY;"

Invoke-Sql $beta "allow insert policy" @"
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'allow insert' AND tablename = 'waitlist') THEN
    EXECUTE 'CREATE POLICY "allow insert" ON waitlist FOR INSERT WITH CHECK (true)';
  END IF;
END $$;
"@

Invoke-Sql $beta "no select policy" @"
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'no select' AND tablename = 'waitlist') THEN
    EXECUTE 'CREATE POLICY "no select" ON waitlist FOR SELECT USING (false)';
  END IF;
END $$;
"@

Write-Host ""
Write-Host "=== Verify ==="
$body = @{ query = "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename" } | ConvertTo-Json
Write-Host "PROD tables:"
(Invoke-RestMethod -Uri "https://api.supabase.com/v1/projects/$prod/database/query" -Method POST -Headers $headers -Body $body) | ForEach-Object { Write-Host "  $($_.tablename)" }
Write-Host "BETA tables:"
(Invoke-RestMethod -Uri "https://api.supabase.com/v1/projects/$beta/database/query" -Method POST -Headers $headers -Body $body) | ForEach-Object { Write-Host "  $($_.tablename)" }
