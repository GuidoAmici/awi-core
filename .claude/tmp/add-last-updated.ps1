Set-Location 'D:\GitHub\GuidoAmici\second-brain'
$date = '2026-03-09'
$updated = 0
$skipped = 0

Get-ChildItem 'info' -Recurse -Filter '*.md' | ForEach-Object {
    $filePath = $_.FullName
    $content = Get-Content $filePath -Raw -Encoding UTF8
    if (-not ($content -match '^---')) { return }
    if ($content -match 'last-updated:') { $skipped++; return }

    $lines = $content -split "`n"
    $closingIdx = -1
    for ($i = 1; $i -lt $lines.Count; $i++) {
        if ($lines[$i].Trim() -eq '---') { $closingIdx = $i; break }
    }
    if ($closingIdx -gt 0) {
        $before = $lines[0..($closingIdx-1)]
        $after  = $lines[$closingIdx..($lines.Count-1)]
        $newLines = $before + "last-updated: $date" + $after
        $newContent = $newLines -join "`n"
        Set-Content -Path $filePath -Value $newContent -Encoding UTF8 -NoNewline
        $updated++
    }
}
Write-Host "Updated: $updated, Skipped: $skipped"
