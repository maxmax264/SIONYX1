# Step 2 (clean version). Run from inside sionyx-web. Read-only, no changes made.

Write-Host "=================================================="
Write-Host "  Is repo currently public or private on GitHub?"
Write-Host "=================================================="
git remote -v
Write-Host ""

Write-Host "=================================================="
Write-Host "  Total commit count on this repo"
Write-Host "=================================================="
git --no-pager log --all --oneline | Measure-Object -Line
Write-Host ""

Write-Host "=================================================="
Write-Host "  Does sionyx-kiosk-wpf folder exist as nested git repo (submodule) inside sionyx-web?"
Write-Host "=================================================="
Test-Path "sionyx-kiosk-wpf\.git"
Write-Host ""

Write-Host "=================================================="
Write-Host "  All commits (hash + date + message) that touched a file literally named 'env' or 'env.example'"
Write-Host "=================================================="
git --no-pager log --all --follow --pretty=format:"%h %ad %s" --date=short -- env
Write-Host ""
git --no-pager log --all --follow --pretty=format:"%h %ad %s" --date=short -- env.example
Write-Host ""

Write-Host "=================================================="
Write-Host "  Is 'env' currently present in the working folder right now?"
Write-Host "=================================================="
Test-Path "env"
Write-Host ""

Write-Host "  Done. Send this output back (no secrets should appear here)."
