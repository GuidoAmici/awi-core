$base = "D:/GitHub/GuidoAmici/second-brain"
$today = "2026-03-19"

Write-Host "=== DUE TODAY ==="
Get-ChildItem "$base/info/organization/tasks/*.md" | ForEach-Object {
    $c = Get-Content $_.FullName -Raw
    if ($c -match "due: $today") { $_.FullName }
}

Write-Host "=== OVERDUE ==="
Get-ChildItem "$base/info/organization/tasks/*.md" | ForEach-Object {
    $c = Get-Content $_.FullName -Raw
    if ($c -match "due: 2026-03-1[0-8]|due: 2026-03-0|due: 2026-02|due: 2026-01|due: 2025") { $_.FullName }
}

Write-Host "=== THIS WEEK (through 2026-03-22) ==="
Get-ChildItem "$base/info/organization/tasks/*.md" | ForEach-Object {
    $c = Get-Content $_.FullName -Raw
    if ($c -match "due: 2026-03-2[0-2]") { $_.FullName }
}

Write-Host "=== ACTIVE PROJECTS ==="
Get-ChildItem "$base/info/organization/projects/*.md" | ForEach-Object {
    $c = Get-Content $_.FullName -Raw
    if ($c -match "status: active") { $_.FullName }
}
