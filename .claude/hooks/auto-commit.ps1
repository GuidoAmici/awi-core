# Auto-commit vault changes after Write/Edit/Bash(mv) operations
$InputText = [Console]::In.ReadToEnd()
$data = $InputText | ConvertFrom-Json
$ToolName = if ($data.tool_name) { $data.tool_name } else { "" }
$FilePath = if ($data.tool_input.file_path) { $data.tool_input.file_path } elseif ($data.tool_input.filePath) { $data.tool_input.filePath } else { "" }
$Command = if ($data.tool_input.command) { $data.tool_input.command } else { "" }

# Handle Bash tool: only act on mv / git mv commands
if ($ToolName -eq "Bash") {
    if ($Command -match '(^|[;&|\s])(git\s+mv|mv)\s') {
        $VaultRoot = (Get-Item $PSScriptRoot).Parent.Parent.FullName
        Set-Location $VaultRoot
        git diff --cached --quiet 2>$null
        if ($LASTEXITCODE -ne 0) {
            $Summary = (git diff --cached --name-status | ForEach-Object { ($_ -split "\t")[-1] } | Split-Path -Leaf) -join ", "
            git commit -m "cos: move/rename - $Summary"
        }
    }
    exit 0
}

if (-not $FilePath) { exit 0 }

# Derive vault root from script location (script is at .claude/hooks/)
$VaultRoot = (Get-Item $PSScriptRoot).Parent.Parent.FullName

# Normalize paths for comparison
$NormFile = $FilePath.Replace("\", "/")
$NormRoot = $VaultRoot.Replace("\", "/")
if (-not $NormFile.StartsWith($NormRoot)) { exit 0 }

$RelPath = $NormFile.Substring($NormRoot.Length + 1)

Set-Location $VaultRoot

# Skip gitignored files
$ignored = git check-ignore -q $FilePath 2>$null
if ($LASTEXITCODE -eq 0) { exit 0 }

$parts = $RelPath -split "/"
$Filename = [System.IO.Path]::GetFileNameWithoutExtension($RelPath)

$typeMap = @{
    "tasks" = "task"; "projects" = "project";
    "daily" = "daily plan"; "weekly" = "weekly summary"; "outputs" = "output";
    "context" = "context"; "people" = "person"; "ideas" = "idea";
    "products" = "product"; "planning" = "planning"; "wiki" = "wiki";
    "second-brain-core" = "second-brain-core"; "user-profile-inference" = "user-profile-inference"
}

# Derive type from path
if ($parts[0] -eq "_documents") {
    $SubFolder = if ($parts.Length -gt 1) { $parts[1] } else { "documents" }
    if ($SubFolder -eq "organization" -and $parts.Length -gt 2) { $SubFolder = $parts[2] }
    $Type = if ($typeMap.ContainsKey($SubFolder)) { $typeMap[$SubFolder] } else { $SubFolder }
} else {
    $Type = $parts[0]
}

$hasDiff = $false
git diff --quiet $FilePath 2>$null
if ($LASTEXITCODE -ne 0) { $hasDiff = $true }
git diff --cached --quiet $FilePath 2>$null
if ($LASTEXITCODE -ne 0) { $hasDiff = $true }

if ($hasDiff) {
    git add $FilePath
    git commit -m "cos: update $Type - $Filename"
} else {
    git ls-files --error-unmatch $FilePath 2>$null
    if ($LASTEXITCODE -ne 0) {
        git add $FilePath
        git commit -m "cos: new $Type - $Filename"
    }
}

exit 0
