# Step 5 - check .env content right before the Registry migration. Run from sionyx-web.
# IMPORTANT: this WILL print secret values to your own screen. Do not paste this output back to Claude.
# Only tell Claude, in your own words, whether values look real/filled-in or empty, and which variable names appear.

Write-Host "=== Parent commit of a6b68ac (the .env file as it was right before migration) ==="
git --no-pager log -1 --pretty=format:"%h %ad %s" --date=short a6b68ac^
Write-Host ""
Write-Host "=== Attempting to show .env content at that parent commit ==="
git --no-pager show a6b68ac^:.env 2>&1
Write-Host ""
Write-Host "=== If that path failed, try other likely locations ==="
git --no-pager show a6b68ac^:sionyx-kiosk-wpf/.env 2>&1
Write-Host ""
git --no-pager show a6b68ac~1 --stat 2>&1 | Select-String -Pattern "env"
Write-Host ""
Write-Host "Done. Remember: do not paste the actual values back into the chat."
