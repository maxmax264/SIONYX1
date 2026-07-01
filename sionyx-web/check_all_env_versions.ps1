# Step 4 - find every version of 'env' that ever existed. Run from sionyx-web. Read-only.

Write-Host "=== Every commit that ever touched a file named 'env' (added/modified/deleted) ==="
git --no-pager log --all --pretty=format:"%h|%ad|%s" --date=short --name-status -- env | Select-String -Pattern "env|^[0-9a-f]{7}\|"
Write-Host ""

Write-Host "=== For comparison: same search but using full path matching (in case 'env' lived nested) ==="
git --no-pager log --all --pretty=format:"%h|%ad|%s" --date=short --name-only | Select-String -Pattern "\benv\b" -Context 1,0

Write-Host ""
Write-Host "Done."
