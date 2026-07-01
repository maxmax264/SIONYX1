# Step B - Install git-filter-repo. Run from anywhere (e.g. SIONYX-clean folder).

Write-Host "=== Installing git-filter-repo via pip ==="
pip install git-filter-repo
Write-Host ""

Write-Host "=== Verifying installation ==="
git filter-repo --version
Write-Host ""
Write-Host "If you see a version number above, it's installed correctly."
Write-Host "If you see an error, tell Claude the exact error message."
