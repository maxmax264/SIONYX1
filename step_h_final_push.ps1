# Step H - final verification + force push everything. Run from SIONYX-clean.

Write-Host "=== Final scan: any secrets left? (PAT, set-env.ps1 file, env, env.example) ==="
$allObjects = git rev-list --all --objects
$suspicious = $allObjects | Where-Object { $_ -match "(^|\s)env$|(^|\s)env\.example$|set-env\.ps1$" }
if ($suspicious) {
    Write-Host "STILL FOUND:"
    $suspicious
} else {
    Write-Host "CLEAN - none of env, env.example, or set-env.ps1 found anywhere."
}
Write-Host ""

Write-Host "=== Re-adding origin remote ==="
git remote add origin https://github.com/maxmax264/SIONYX1.git
git remote -v
Write-Host ""

Write-Host "=== Force pushing ALL branches ==="
git push origin --force --all
Write-Host ""

Write-Host "=== Force pushing ALL tags ==="
git push origin --force --tags
Write-Host ""
Write-Host "Done. Report back full output."
