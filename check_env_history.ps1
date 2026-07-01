# שלב 1: אבחון בלבד - הסקריפט הזה לא משנה שום דבר, רק בודק ומדפיס.
# הרץ אותו מתוך תיקיית הריפו עצמו (sionyx-kiosk-wpf או sionyx-web), לא מתוך SIONYX-clean.

Write-Host "=================================================="
Write-Host "  בדיקת חשיפת .env בריפו: $(Split-Path -Leaf (Get-Location))"
Write-Host "=================================================="
Write-Host ""

Write-Host "--- 1) קבצי env בתיקייה הנוכחית (working tree), לא בתוך .git ---"
$envFiles = Get-ChildItem -Recurse -Depth 2 -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match "env" -and $_.FullName -notmatch "\\\.git\\" }
if ($envFiles) {
    $envFiles | Select-Object FullName, Length, LastWriteTime | Format-Table -AutoSize
} else {
    Write-Host "(לא נמצא קובץ env בתיקייה הנוכחית)"
}
Write-Host ""

Write-Host "--- 2) האם git עוקב (tracked) אחרי קובץ env? ---"
$tracked = git ls-files | Select-String -Pattern "env" -CaseSensitive:$false
if ($tracked) {
    Write-Host "אזהרה: git עוקב אחרי הקבצים הבאים:"
    $tracked
} else {
    Write-Host "(git לא עוקב אחרי שום קובץ עם 'env' בשם - טוב סימן)"
}
Write-Host ""

Write-Host "--- 3) האם env מופיע בהיסטוריה (בכל commit, בכל branch)? הבדיקה הקריטית ---"
$historyHits = git log --all --full-history --pretty=format:"COMMIT:%h %ad" --date=short --name-only |
    Select-String -Pattern "env" -CaseSensitive:$false -Context 1,0
if ($historyHits) {
    Write-Host "אזהרה: env נמצא בהיסטוריית git:"
    $historyHits
} else {
    Write-Host "(env לא נמצא בשום commit בהיסטוריה - מעולה!)"
}
Write-Host ""

Write-Host "--- 4) כל שמות הקבצים שאי פעם נוספו להיסטוריה ומכילים 'env' ---"
$allAdded = git log --all --pretty=format: --name-only --diff-filter=A 2>$null |
    Sort-Object -Unique |
    Select-String -Pattern "env" -CaseSensitive:$false
if ($allAdded) {
    $allAdded
} else {
    Write-Host "(לא נמצאו קבצים עם 'env' בשם בכל ההיסטוריה)"
}
Write-Host ""

Write-Host "--- 5) .gitignore - קיים? כולל env? ---"
if (Test-Path ".gitignore") {
    Write-Host "[.gitignore קיים, שורות רלוונטיות:]"
    $giHits = Select-String -Path ".gitignore" -Pattern "env" -CaseSensitive:$false
    if ($giHits) { $giHits } else { Write-Host "אזהרה: .gitignore קיים אבל לא מכיל 'env'!" }
} else {
    Write-Host "אזהרה: אין קובץ .gitignore בריפו הזה!"
}
Write-Host ""

Write-Host "=================================================="
Write-Host "  סיום בדיקה. שלח את כל הפלט הזה בחזרה."
Write-Host "=================================================="
