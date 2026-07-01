# Step 3 - direct check against known commit. Run from sionyx-web. Read-only.

Write-Host "=== Does commit e78c582 contain a file named exactly 'env'? ==="
git --no-pager show e78c582 --name-only | Select-String -Pattern "^env$"
Write-Host ""

Write-Host "=== Search ALL history for any blob path that is exactly 'env' (top level) ==="
git --no-pager log --all --pretty=format:"COMMIT:%h %ad" --date=short --name-status | Select-String -Pattern "env" -Context 1,0
Write-Host ""

Write-Host "=== Confirm: is 'env' tracked in the current HEAD tree? ==="
git ls-tree -r HEAD --name-only | Select-String -Pattern "^env$|env\.example$"
Write-Host ""

Write-Host "=== Show first few lines of git log for commit e78c582 (just to confirm hash is real) ==="
git --no-pager log -1 e78c582

Write-Host ""
Write-Host "Done."
