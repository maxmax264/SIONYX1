# Step 7 (FIXED) - comprehensive scan across all history. Run from sionyx-web.
# Output is just paths/hashes - safe to paste back.

Write-Host "=== Method A: git log --name-status, simple substring match on 'env' ==="
git --no-pager log --all --pretty=format:"COMMIT:%h|%ad|%s" --date=short --name-status |
    Select-String -SimpleMatch "env"
Write-Host ""
Write-Host "--- END Method A ---"
Write-Host ""

Write-Host "=== Method B: git rev-list --objects (lists every blob path ever, across all history) ==="
$allObjects = git rev-list --all --objects
$envObjects = $allObjects | Where-Object { $_ -match "env" }
Write-Host "Total objects scanned: $($allObjects.Count)"
Write-Host "Objects with 'env' in path:"
$envObjects
Write-Host ""
Write-Host "--- END Method B ---"
