# Step 1: Diagnostic only - this script does not change anything, only checks and prints.
# Run this from inside the repo folder itself (sionyx-kiosk-wpf or sionyx-web), NOT from SIONYX-clean.

$repoName = Split-Path -Leaf (Get-Location)
Write-Host "=================================================="
Write-Host "  .env exposure check for repo: $repoName"
Write-Host "=================================================="
Write-Host ""

Write-Host "--- 1) env files in current working tree (not inside .git) ---"
$envFiles = Get-ChildItem -Recurse -Depth 2 -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match "env" -and $_.FullName -notmatch "\\\.git\\" }
if ($envFiles) {
    $envFiles | Select-Object FullName, Length, LastWriteTime | Format-Table -AutoSize
} else {
    Write-Host "(no env file found in current working tree)"
}
Write-Host ""

Write-Host "--- 2) Is git tracking any env file right now? ---"
$tracked = git ls-files | Select-String -Pattern "env" -CaseSensitive:$false
if ($tracked) {
    Write-Host "WARNING: git is tracking these files:"
    $tracked
} else {
    Write-Host "(git is not tracking any file with 'env' in the name - good sign)"
}
Write-Host ""

Write-Host "--- 3) Does env appear anywhere in history (all commits, all branches)? CRITICAL CHECK ---"
$historyHits = git log --all --full-history --pretty=format:"COMMIT:%h %ad" --date=short --name-only |
    Select-String -Pattern "env" -CaseSensitive:$false -Context 1,0
if ($historyHits) {
    Write-Host "WARNING: env found in git history:"
    $historyHits
} else {
    Write-Host "(env not found in any commit in history - excellent!)"
}
Write-Host ""

Write-Host "--- 4) All filenames ever added to history that contain 'env' ---"
$allAdded = git log --all --pretty=format: --name-only --diff-filter=A 2>$null |
    Sort-Object -Unique |
    Select-String -Pattern "env" -CaseSensitive:$false
if ($allAdded) {
    $allAdded
} else {
    Write-Host "(no files with 'env' in the name found across all history)"
}
Write-Host ""

Write-Host "--- 5) .gitignore - exists? includes env? ---"
if (Test-Path ".gitignore") {
    Write-Host "[.gitignore exists, relevant lines:]"
    $giHits = Select-String -Path ".gitignore" -Pattern "env" -CaseSensitive:$false
    if ($giHits) { $giHits } else { Write-Host "WARNING: .gitignore exists but does not contain 'env'!" }
} else {
    Write-Host "WARNING: no .gitignore file in this repo!"
}
Write-Host ""

Write-Host "=================================================="
Write-Host "  Check complete. Send back all of this output."
Write-Host "=================================================="
