# Step A - BACKUP + prerequisite check. Run from inside sionyx-web (or wherever SIONYX1 is cloned).
# This makes a full bare backup clone before we touch anything destructive.

Write-Host "=================================================="
Write-Host "  1) Checking if git-filter-repo is installed"
Write-Host "=================================================="
$filterRepoCheck = git filter-repo --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "git-filter-repo IS installed: $filterRepoCheck"
} else {
    Write-Host "git-filter-repo is NOT installed."
    Write-Host "Install it with one of these methods:"
    Write-Host "  Option A (pip):  pip install git-filter-repo"
    Write-Host "  Option B (manual): download git-filter-repo script from https://github.com/newren/git-filter-repo"
    Write-Host "  Option C (if you have Python): python -m pip install git-filter-repo"
}
Write-Host ""

Write-Host "=================================================="
Write-Host "  2) Creating a full BARE backup clone (safety net)"
Write-Host "=================================================="
$repoRoot = git rev-parse --show-toplevel
$repoName = Split-Path -Leaf $repoRoot
$backupPath = "C:\Users\user\Desktop\SIONYX-BACKUP-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
Write-Host "Repo root detected at: $repoRoot"
Write-Host "Creating backup at: $backupPath"

git clone --mirror "$repoRoot" "$backupPath"

if (Test-Path "$backupPath") {
    Write-Host ""
    Write-Host "BACKUP CREATED SUCCESSFULLY at: $backupPath"
    Write-Host "This is a full mirror of your repo history, untouched. Keep it safe until cleanup is verified."
} else {
    Write-Host "WARNING: backup may have failed. Do NOT proceed until this is fixed."
}
Write-Host ""

Write-Host "Done. Report back: (1) is git-filter-repo installed, (2) did the backup succeed."
