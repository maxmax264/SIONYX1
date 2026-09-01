# ============================================================
# עדכון Cloud Function resetUserPassword: 6 -> 4 תווים
# עם אותה טרנספורמציה בדיוק כמו בצד ה-C# (חייב להיות זהה!)
# ============================================================
cd C:\Users\user\Desktop\SIONYX-clean

$results = @()

function Apply-Edit($path, $old, $new, $label) {
    $c = Get-Content $path -Raw
    $count = ([regex]::Matches($c, [regex]::Escape($old))).Count
    if ($count -ne 1) {
        Write-Host "[FAIL] $label -- נמצאו $count התאמות (צריך 1) ב-$path" -ForegroundColor Red
        $script:results += "FAIL: $label"
        return $false
    }
    $c = $c.Replace($old, $new)
    [System.IO.File]::WriteAllText((Resolve-Path $path), $c, [System.Text.UTF8Encoding]::new($false))
    Write-Host "[OK] $label" -ForegroundColor Green
    $script:results += "OK: $label"
    return $true
}

$p = "functions\index.js"

Apply-Edit $p 'exports.resetUserPassword = onCall(async (request) => {' @'
/**
 * Ensures the password sent to Firebase Auth meets its hard 6-char floor.
 * Existing 6+ char passwords pass through unchanged (backward compatible);
 * shorter PINs get a fixed prefix. Must match AuthService.cs's version exactly.
 */
function toFirebasePassword(raw) {
  return raw.length >= 6 ? raw : `px_${raw}`;
}

exports.resetUserPassword = onCall(async (request) => {
'@ "index.js: הוספת helper toFirebasePassword"

Apply-Edit $p 'if (newPassword.length < 6) {' 'if (newPassword.length < 4) {' "index.js: סף ולידציה"
Apply-Edit $p '"הסיסמה חייבת להכיל לפחות 6 תווים"' '"הסיסמה חייבת להכיל לפחות 4 תווים"' "index.js: הודעת שגיאה"
Apply-Edit $p @'
    await admin.auth().updateUser(userId, {
      password: newPassword,
    });
'@ @'
    await admin.auth().updateUser(userId, {
      password: toFirebasePassword(newPassword),
    });
'@ "index.js: updateUser + טרנספורמציה"

Write-Host ""
Write-Host "=== סיכום ===" -ForegroundColor Cyan
$results | ForEach-Object { Write-Host $_ }
if ($results -match "^FAIL") {
    Write-Host "יש כשלונות - שלח לי את הפלט, אל תעשה deploy" -ForegroundColor Red
} else {
    Write-Host "בוצע. עכשיו תריץ טסטים לפני deploy:" -ForegroundColor Green
    Write-Host "  cd functions" -ForegroundColor Yellow
    Write-Host "  npm test" -ForegroundColor Yellow
}
