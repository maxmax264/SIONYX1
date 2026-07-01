# Step D - Final steps. Run from C:\Users\user\Desktop\SIONYX-clean (repo root).

Write-Host "=================================================="
Write-Host "  1) Adding 'env' (no dot) protection to .gitignore"
Write-Host "=================================================="
$gitignoreContent = Get-Content ".gitignore" -Raw
if ($gitignoreContent -notmatch "(?m)^env$") {
    Add-Content ".gitignore" "`n# Plain 'env' file (no dot) - contains real Firebase config, never commit`nenv`n"
    Write-Host "Added 'env' to .gitignore"
} else {
    Write-Host "'env' already in .gitignore, skipping"
}
Write-Host ""

Write-Host "=================================================="
Write-Host "  2) Committing the .gitignore update"
Write-Host "=================================================="
git add .gitignore
git commit -m "chore: ensure plain env file is gitignored"
Write-Host ""

Write-Host "=================================================="
Write-Host "  3) Re-adding the origin remote"
Write-Host "=================================================="
git remote add origin https://github.com/maxmax264/SIONYX1.git
git remote -v
Write-Host ""

Write-Host "=================================================="
Write-Host "  4) Force pushing the cleaned history to GitHub"
Write-Host "=================================================="
Write-Host "This will overwrite ALL history on GitHub with the cleaned version."
git push origin --force --all
git push origin --force --tags
Write-Host ""

Write-Host "Done. Report back the full output."
