# scripts/vendor_docrag.ps1
# Vendor DocRAG-MD source into analysis-target/ for Bob analysis.
# Usage: from repo root, .\scripts\vendor_docrag.ps1 -SourcePath "..\docrag-md-source"

param(
    [Parameter(Mandatory=$true)]
    [string]$SourcePath
)

if (-not (Test-Path $SourcePath)) {
    Write-Error "Source path '$SourcePath' does not exist. Clone DocRAG-MD first."
    exit 1
}

if (-not (Test-Path "$SourcePath\src")) {
    Write-Error "Source path '$SourcePath' has no src/ folder. Is this really DocRAG-MD?"
    exit 1
}

Write-Host "Vendoring DocRAG-MD source into analysis-target/..." -ForegroundColor Cyan

# Create target
if (Test-Path "analysis-target") {
    $confirm = Read-Host "analysis-target/ already exists. Overwrite? (y/N)"
    if ($confirm -ne "y") { exit 0 }
    Remove-Item -Recurse -Force analysis-target
}
New-Item -ItemType Directory -Path analysis-target | Out-Null

# Copy src tree
Write-Host "Copying src/..." -ForegroundColor Gray
xcopy /E /I /Y "$SourcePath\src" "analysis-target\src" | Out-Null

# Copy optional metadata files
foreach ($f in @("README.md", "pyproject.toml", "requirements.txt", "LICENSE")) {
    if (Test-Path "$SourcePath\$f") {
        $dest = if ($f -eq "LICENSE") { "analysis-target\ORIGINAL_LICENSE" } else { "analysis-target\$f" }
        Copy-Item "$SourcePath\$f" $dest
        Write-Host "  ✓ $f" -ForegroundColor Gray
    }
}

# Create NOTICE
$notice = @"
# analysis-target/

This directory contains a vendored snapshot of DocRAG-MD, a Master's thesis
project built at Telecom Paris by a team of 5 (Ahmed, Tahiana Andriambahoaka,
Oussama Rhouma, Mohamed Khalil Ounis, Mohamed Amar) over 4 months.

It is included **read-only** as the analysis subject for IBM Bob during the
BobRAG-MD hackathon submission. Bob did not author the code in this directory.

The Bob-authored refactor in this submission lives on a feature branch within
the bobrag-md repository only; no changes flow back to the original DocRAG-MD repo.

Original repository: https://github.com/<your-username>/docrag-md
Original license: see ORIGINAL_LICENSE
"@
$notice | Out-File -Encoding UTF8 "analysis-target\NOTICE.md"

# Clean caches
Get-ChildItem -Recurse -Path "analysis-target" -Filter "__pycache__" -Directory | Remove-Item -Recurse -Force
Get-ChildItem -Recurse -Path "analysis-target" -Filter "*.pyc" | Remove-Item -Force

# Stats
$pyCount = (Get-ChildItem -Recurse -Path "analysis-target\src" -Filter "*.py" | Measure-Object).Count
Write-Host ""
Write-Host "Vendored $pyCount .py files into analysis-target/src/" -ForegroundColor Green

if ($pyCount -gt 60) {
    Write-Warning "More than 60 Python files vendored. Consider trimming notebooks, tests, or data dumps."
}
if ($pyCount -lt 5) {
    Write-Warning "Fewer than 5 Python files vendored. Check your source path."
}

Write-Host ""
Write-Host "Done. Next: git add analysis-target/ && git commit -m 'Vendor DocRAG-MD as analysis target'"
