# Step C - THE ACTUAL CLEANUP. Run from C:\Users\user\Desktop\SIONYX-clean (repo root).
# This rewrites history. Your backup is at SIONYX-BACKUP-20260628-183643 (mirror clone) if anything goes wrong.

Write-Host "=================================================="
Write-Host "  Before/after commit count check"
Write-Host "=================================================="
Write-Host "Commit count BEFORE cleanup:"
git --no-pager log --all --oneline | Measure-Object -Line
Write-Host ""

Write-Host "=================================================="
Write-Host "  Running git filter-repo to strip env and env.example from ALL history"
Write-Host "=================================================="
git filter-repo --path env --path env.example --invert-paths --force

Write-Host ""
Write-Host "=================================================="
Write-Host "  Verification: searching for env/env.example anywhere in history NOW"
Write-Host "=================================================="
$allObjects = git rev-list --all --objects
$envObjects = $allObjects | Where-Object { $_ -match "(^|\s)env$|(^|\s)env\.example$" }
if ($envObjects) {
    Write-Host "WARNING - still found:"
    $envObjects
} else {
    Write-Host "SUCCESS: env and env.example are completely gone from history."
}
Write-Host ""

Write-Host "=================================================="
Write-Host "  Commit count AFTER cleanup (hashes will all be different - this is expected)"
Write-Host "=================================================="
git --no-pager log --all --oneline | Measure-Object -Line
Write-Host ""

Write-Host "=================================================="
Write-Host "  Current remote status (filter-repo removes the origin remote as a safety measure)"
Write-Host "=================================================="
git remote -v
Write-Host "(If empty, this is EXPECTED - filter-repo removes remotes to prevent accidental push. We will re-add it next.)"
Write-Host ""
Write-Host "Done. Report back the full output, especially the verification section."
