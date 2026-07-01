# Run from C:\Users\user\Desktop\SIONYX-clean
# Shows truncated values (first ~15 chars) to check if real or placeholder, without exposing full secrets

Write-Host "=== set-env.ps1.example content (TRUNCATED values for safety) ==="
git show fix/secret-hygiene:sionyx-kiosk-wpf/set-env.ps1.example 2>$null | ForEach-Object {
    if ($_ -match '^\$env:([A-Za-z_][A-Za-z0-9_]*)\s*=\s*"(.{0,15})') {
        Write-Host "$($matches[1]) = $($matches[2])..."
    } elseif ($_ -match '^\$env:([A-Za-z_][A-Za-z0-9_]*)') {
        Write-Host "$($matches[1]) = (no value shown / different format)"
    }
}
Write-Host ""
Write-Host "Done. This output is truncated/safe to paste."
