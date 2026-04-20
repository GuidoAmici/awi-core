$base = "D:/GitHub/GuidoAmici/second-brain/info/organization"

# Files with auth-unificado references
$files = @(
    "$base/daily/2026-03-19.md",
    "$base/daily/2026-03-12.md",
    "$base/daily/2026-03-11.md",
    "$base/daily/2026-03-10.md",
    "$base/daily/2026-03-09.md",
    "$base/daily/2026-03-01.md",
    "$base/daily/2026-03-02.md",
    "$base/projects/newhaze-ui.md",
    "$base/projects/newhaze-outer-panel.md",
    "$base/planning/2026-Q1.md",
    "$base/tasks/separate-panel-tasks.md",
    "$base/tasks/publish-google-oauth-consent-screen.md",
    "$base/tasks/profile-picture-upload.md",
    "$base/tasks/feature-pipeline-tracker.md",
    "$base/tasks/define-environment-strategy.md",
    "$base/weekly/2026-W10.md"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw -Encoding UTF8
        $updated = $content -replace 'auth-unificado', 'sso'
        if ($content -ne $updated) {
            Set-Content $file -Value $updated -Encoding UTF8 -NoNewline
            Write-Host "Updated: $file"
        }
    }
}

# Rename the project file
$old = "$base/projects/auth-unificado.md"
$new = "$base/projects/sso.md"
if (Test-Path $old) {
    Rename-Item $old $new
    Write-Host "Renamed: auth-unificado.md -> sso.md"
}
