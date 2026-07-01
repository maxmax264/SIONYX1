# Comprehensive env scan for sionyx-kiosk-wpf repo. Run from inside that repo folder.
# Output is just paths/hashes/remote info - safe to paste back.

Write-Host "=================================================="
Write-Host "  Remote info"
Write-Host "=================================================="
git remote -v
Write-Host ""

Write-Host "=================================================="
Write-Host "  Total commit count"
Write-Host "=================================================="
git --no-pager log --all --oneline | Measure-Object -Line
Write-Host ""

Write-Host "=================================================="
Write-Host "  Method A: git log --name-status, substring match on 'env'"
Write-Host "=================================================="
git --no-pager log --all --pretty=format:"COMMIT:%h|%ad|%s" --date=short --name-status |
    Select-String -SimpleMatch "env"
Write-Host ""

Write-Host "=================================================="
Write-Host "  Method B: git rev-list --objects (every blob path ever, all history)"
Write-Host "=================================================="
$allObjects = git rev-list --all --objects
$envObjects = $allObjects | Where-Object { $_ -match "env" }
Write-Host "Total objects scanned: $($allObjects.Count)"
Write-Host "Objects with 'env' in path:"
$envObjects
Write-Host ""

Write-Host "=================================================="
Write-Host "  Is any env file tracked in current HEAD?"
Write-Host "=================================================="
git ls-tree -r HEAD --name-only | Select-String -Pattern "env"
Write-Host ""

Write-Host "=================================================="
Write-Host "  .gitignore - exists? includes env?"
Write-Host "=================================================="
if (Test-Path ".gitignore") {
    Select-String -Path ".gitignore" -Pattern "env"
} else {
    Write-Host "WARNING: no .gitignore!"
}
Write-Host ""
Write-Host "Done."
