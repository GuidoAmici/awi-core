$repos = @('newhaze-outer-panel','newhaze-inner-panel','newhaze-ui','newhaze-learn','newhaze-api')
foreach ($repo in $repos) {
  $path = "D:/GitHub/GuidoAmici/second-brain/apps/$repo"
  Set-Location $path
  git add .gitignore
  git commit -m "fix: correct .gitignore pattern for agent context files"
  git push origin dev
  Write-Host "Pushed: $repo"
}
