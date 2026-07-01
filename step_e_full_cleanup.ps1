# Step E - COMPREHENSIVE cleanup covering ALL branches (including ones not previously fetched locally)
# Run from C:\Users\user\Desktop\SIONYX-clean (repo root).

Write-Host "=================================================="
Write-Host "  1) Fetching ALL remote branches and tags (including ones we missed before)"
Write-Host "=================================================="
git fetch origin '+refs/heads/*:refs/remotes/origin/*' '+refs/tags/*:refs/tags/*'
Write-Host ""

Write-Host "=================================================="
Write-Host "  2) Creating local tracking branches for EVERY remote branch"
Write-Host "=================================================="
git branch -a
foreach ($remoteBranch in (git branch -r | Where-Object { $_ -notmatch "HEAD" })) {
    $remoteBranch = $remoteBranch.Trim()
    $localName = $remoteBranch -replace "^origin/", ""
    git show-ref --verify --quiet "refs/heads/$localName"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Creating local branch: $localName from $remoteBranch"
        git branch --track $localName $remoteBranch 2>&1
    } else {
        Write-Host "Local branch already exists: $localName"
    }
}
Write-Host ""

Write-Host "=================================================="
Write-Host "  3) Verify - listing all local branches now"
Write-Host "=================================================="
git branch
Write-Host ""

Write-Host "=================================================="
Write-Host "  4) Running filter-repo AGAIN across ALL branches/tags this time"
Write-Host "=================================================="
git filter-repo --path env --path env.example --invert-paths --force
Write-Host ""

Write-Host "=================================================="
Write-Host "  5) Verification across ALL local branches"
Write-Host "=================================================="
$allObjects = git rev-list --all --objects
$envObjects = $allObjects | Where-Object { $_ -match "(^|\s)env$|(^|\s)env\.example$" }
if ($envObjects) {
    Write-Host "STILL FOUND (problem):"
    $envObjects
} else {
    Write-Host "SUCCESS: env and env.example fully removed from ALL branches/tags."
}
Write-Host ""
Write-Host "Done. Report back full output."
