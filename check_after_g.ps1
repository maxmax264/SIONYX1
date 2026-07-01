# Diagnostic after step G. Run from C:\Users\user\Desktop\SIONYX-clean.

Write-Host "=== Current local branches ==="
git branch
Write-Host ""

Write-Host "=== Commit count per branch ==="
foreach ($b in (git branch --format='%(refname:short)')) {
    $count = (git log $b --oneline | Measure-Object -Line).Lines
    Write-Host "$b : $count commits"
}
Write-Host ""

Write-Host "=== Does fix/rtdb-rules-regressions or fix/secret-hygiene still exist locally? ==="
git branch | Select-String -Pattern "fix/"
Write-Host ""

Write-Host "=== Content of set-env.ps1.example variable NAMES only (safe - no values) ==="
$content = git show HEAD:sionyx-kiosk-wpf/set-env.ps1.example 2>$null
if ($content) {
    $content | Select-String -Pattern '\$env:[A-Za-z_][A-Za-z0-9_]*' -AllMatches | ForEach-Object { $_.Matches.Value } | Sort-Object -Unique
} else {
    Write-Host "(file not found at HEAD on current branch, checking all branches)"
    foreach ($b in (git branch --format='%(refname:short)')) {
        $c = git show "${b}:sionyx-kiosk-wpf/set-env.ps1.example" 2>$null
        if ($c) {
            Write-Host "--- found on branch $b ---"
            $c | Select-String -Pattern '\$env:[A-Za-z_][A-Za-z0-9_]*' -AllMatches | ForEach-Object { $_.Matches.Value } | Sort-Object -Unique
        }
    }
}
Write-Host ""
Write-Host "Done."
