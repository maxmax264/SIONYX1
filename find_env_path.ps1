# Step 6 - find exact path of any .env-like file at that point in history. Run from sionyx-web.
# Output here is just file PATHS, not content - safe to paste back.

Write-Host "=== Full file tree at commit a6b68ac^ (parent), filtered for 'env' ==="
git --no-pager ls-tree -r a6b68ac^ --name-only | Select-String -Pattern "env"
Write-Host ""

Write-Host "=== Full file tree at commit a6b68ac itself, filtered for 'env' ==="
git --no-pager ls-tree -r a6b68ac --name-only | Select-String -Pattern "env"
Write-Host ""

Write-Host "=== What did commit a6b68ac actually change (stat)? ==="
git --no-pager show a6b68ac --stat | Select-String -Pattern "env|\|"
Write-Host ""

Write-Host "Done."
