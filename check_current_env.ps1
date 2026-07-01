# Run from C:\Users\user\Desktop\SIONYX-clean (the repo root). Read only.
# IMPORTANT: this will print real values currently in the env file to YOUR screen.
# Do NOT paste this output back into the chat. Just tell Claude which variable names have real (non-empty) values.

Write-Host "=== Current content of env (at HEAD, right now) ==="
Get-Content ".\env"
Write-Host ""
Write-Host "=== Current content of env.example ==="
Get-Content ".\env.example"
Write-Host ""
Write-Host "=== .gitignore current content (safe to share - no secrets) ==="
Get-Content ".\.gitignore" | Select-String -Pattern "env"
Write-Host ""
Write-Host "Done. DO NOT paste the env/env.example content above into the chat."
