$token = [System.Environment]::GetEnvironmentVariable('Supabase_PersonalToken', 'User')
if (-not $token) { $token = $env:Supabase_PersonalToken }

# Use Supabase management API to run SQL directly
$projectRef = "rbszzkivswvqagasrvdj"
$sql = "create table if not exists waitlist (email text primary key, created_at timestamptz default now());"

$body = @{ query = $sql } | ConvertTo-Json
$response = Invoke-WebRequest -Uri "https://api.supabase.com/v1/projects/$projectRef/database/query" `
    -Method POST `
    -Headers @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" } `
    -Body $body `
    -UseBasicParsing
Write-Output "Status: $($response.StatusCode)"
Write-Output $response.Content
