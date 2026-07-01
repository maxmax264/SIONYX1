# Step 7 - FINAL comprehensive scan. Run from sionyx-web. Output is just paths/hashes - safe to paste.

Write-Host "=== Every unique file path EVER added/modified that is named exactly '.env' (with dot) ==="
git --no-pager log --all --pretty=format:"COMMIT:%h|%ad" --date=short --name-status |
    Select-String -Pattern "^\.env$|\\\.env$|/\.env$"
Write-Host "(if nothing printed above, '.env' with a dot was never committed as a real file path)"
Write-Host ""

Write-Host "=== Every unique file path EVER added/modified that is named exactly 'env' (no dot) ==="
git --no-pager log --all --pretty=format:"COMMIT:%h|%ad" --date=short --name-status |
    Select-String -Pattern "^env$|\\env$|/env$"
Write-Host ""

Write-Host "=== Every unique blob path across ALL of history containing the substring 'env' as its own path segment ==="
git --no-pager rev-list --all --objects | Select-String -Pattern "(^|/)\.?env$"
Write-Host ""

Write-Host "Done. This is the authoritative list - paste this back."
