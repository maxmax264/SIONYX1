# Step G - Clean set-env.ps1 from ALL history (contains PAT + DB secret).
# Run from C:\Users\user\Desktop\SIONYX-clean (repo root).
# Make sure you've fetched all branches first (we did this in step E).

Write-Host "=================================================="
Write-Host "  Running filter-repo to strip sionyx-kiosk-wpf/set-env.ps1 from ALL history"
Write-Host "=================================================="
git filter-repo --path sionyx-kiosk-wpf/set-env.ps1 --invert-paths --force
Write-Host ""

Write-Host "=================================================="
Write-Host "  Verification: searching for the known secrets anywhere in history NOW"
Write-Host "=================================================="
Write-Host "Checking for GitHub PAT pattern..."
git log --all -p -- '*' 2>$null | Select-String -Pattern "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"
Write-Host "(if nothing above, PAT is gone)"
Write-Host ""

Write-Host "Checking for set-env.ps1 file existing anywhere..."
$allObjects = git rev-list --all --objects
$setEnvObjects = $allObjects | Where-Object { $_ -match "set-env\.ps1" }
if ($setEnvObjects) {
    Write-Host "STILL FOUND:"
    $setEnvObjects
} else {
    Write-Host "SUCCESS: set-env.ps1 completely removed from history."
}
Write-Host ""
Write-Host "Done. Report back full output."
