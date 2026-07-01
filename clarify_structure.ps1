# Clarification script - run from C:\Users\user\Desktop\SIONYX-clean (the PARENT folder)
# Read only - just inspecting structure.

Write-Host "=== Is SIONYX-clean itself a git repo? ==="
Test-Path ".git"
Write-Host ""

Write-Host "=== If yes, what is ITS remote? ==="
if (Test-Path ".git") {
    git remote -v
}
Write-Host ""

Write-Host "=== Is sionyx-web a separate git repo (has its own .git folder)? ==="
Test-Path "sionyx-web\.git"
Write-Host ""

Write-Host "=== Is sionyx-kiosk-wpf a separate git repo? ==="
Test-Path "sionyx-kiosk-wpf\.git"
Write-Host ""

Write-Host "=== List all .git directories found anywhere under SIONYX-clean (depth 3) ==="
Get-ChildItem -Path . -Recurse -Depth 3 -Force -Directory -Filter ".git" -ErrorAction SilentlyContinue | Select-Object FullName
Write-Host ""

Write-Host "=== If SIONYX-clean has its own .git, what is tracked at top level? ==="
if (Test-Path ".git") {
    git ls-tree HEAD --name-only
}
Write-Host ""
Write-Host "Done."
