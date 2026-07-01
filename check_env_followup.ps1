# Step 2: Focused follow-up. Run from inside sionyx-web (same folder as before).
# This does NOT change anything - read only.

Write-Host "=================================================="
Write-Host "  Remote info for this repo"
Write-Host "=================================================="
git remote -v
Write-Host ""

Write-Host "=================================================="
Write-Host "  Show commit e78c582 - what files did it touch?"
Write-Host "=================================================="
git show --stat e78c582
Write-Host ""

Write-Host "=================================================="
Write-Host "  Exact path of 'env' file as tracked in that commit"
Write-Host "=================================================="
git show e78c582 --name-only

Write-Host ""
Write-Host "=================================================="
Write-Host "  Is 'env' (top-level, no path prefix) currently tracked anywhere in history with full path shown?"
Write-Host "=================================================="
git log --all --pretty=format:"COMMIT:%H %ad" --date=short --name-only -- env env.example

Write-Host ""
Write-Host "=================================================="
Write-Host "  Does this repo folder contain a nested .git (submodule) for sionyx-kiosk-wpf?"
Write-Host "=================================================="
Get-ChildItem -Recurse -Directory -Filter ".git" -Force -ErrorAction SilentlyContinue | Select-Object FullName

Write-Host ""
Write-Host "=================================================="
Write-Host "  .gitmodules content if it exists"
Write-Host "=================================================="
if (Test-Path ".gitmodules") {
    Get-Content ".gitmodules"
} else {
    Write-Host "(no .gitmodules file)"
}

Write-Host ""
Write-Host "=================================================="
Write-Host "  First commit and total commit count (to understand repo origin/history)"
Write-Host "=================================================="
git log --all --oneline | Measure-Object -Line
git log --all --reverse --pretty=format:"%h %ad %s" --date=short | Select-Object -First 3

Write-Host ""
Write-Host "  Done. Send this output back."
