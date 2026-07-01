# Step F - Re-add remote and force push ALL branches + tags. Run from SIONYX-clean.

Write-Host "=================================================="
Write-Host "  1) Re-adding origin remote"
Write-Host "=================================================="
git remote add origin https://github.com/maxmax264/SIONYX1.git
git remote -v
Write-Host ""

Write-Host "=================================================="
Write-Host "  2) Force pushing ALL local branches"
Write-Host "=================================================="
git push origin --force --all
Write-Host ""

Write-Host "=================================================="
Write-Host "  3) Force pushing ALL tags"
Write-Host "=================================================="
git push origin --force --tags
Write-Host ""

Write-Host "Done. Report back full output."
