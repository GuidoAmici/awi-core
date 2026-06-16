$repos = @('newhaze-outer-panel','newhaze-inner-panel','newhaze-ui','newhaze-learn','newhaze-api')
foreach ($repo in $repos) {
  $path = "D:/GitHub/GuidoAmici/second-brain/apps/$repo/.gitignore"
  $content = Get-Content $path -Raw
  $fixed = $content -replace '(?m)^\*\*/\*\*/$', "**/.abstract.md`n**/.overview.md"
  Set-Content $path $fixed -NoNewline
  Write-Host "Fixed: $repo"
}
