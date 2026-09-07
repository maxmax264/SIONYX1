# install-aeroadmin.ps1
# שלב תיוג (staging) בלבד ל-AeroAdmin, כגיבוי רביעי אחרי RustDesk/AnyDesk/TeamViewer.
#
# מגבלות אמיתיות של AeroAdmin שאין דרך לעקוף (מתועד ב-aeroadmin.com, לא ניחוש):
#   - אין דגל /silent או /quiet - כל הרצה של ה-exe פותחת חלון.
#   - אין קובץ config/registry קריא עם ה-ID/סיסמה - הכל רק דרך ה-GUI.
#   - אין CLI להגדרת סיסמה מרחוק אחרי ההתקנה.
# בגלל זה השלב האוטומטי היחיד שאפשר לבצע כאן הוא הורדת ה-exe עצמו.
# את ההגדרה החד-פעמית (הוספת גישה ב-Connection > Access rights + קריאת ה-ID)
# מבצע AeroAdminSetupService.cs באמצעות UI Automation, עם החלון מוסתר
# (ProcessStartInfo.WindowStyle=Hidden) כדי שלא יוצג ללקוח בקופה.

$ErrorActionPreference = 'Stop'

$InfoDir      = "C:\ProgramData\SIONYX"
$ExePath      = "$InfoDir\AeroAdmin.exe"
$DownloadUrl  = "https://ulm.aeroadmin.com/AeroAdmin.exe"
$MinValidSize = 1MB   # AeroAdmin.exe is normally several MB - anything smaller is a truncated/corrupt download

Write-Host "[SIONYX] Staging AeroAdmin (portable, on-demand agent)..."

if (-Not (Test-Path $InfoDir)) { New-Item -ItemType Directory -Force -Path $InfoDir | Out-Null }

# שלב 4: ניקוי חכם לפני התקנה/עדכון.
# 1) AeroAdminSetupService.cs מריץ את זה עם חלון מוסתר לצורך הקריאה החד-פעמית
#    של ID/PIN - אם זה נתקע פתוח (UI Automation נכשל בלי לסגור את התהליך),
#    הקובץ נעול ומונע דריסה בהתקנה/עדכון חוזרים. הורגים אותו קודם.
$runningProc = Get-Process -Name "AeroAdmin" -ErrorAction SilentlyContinue
if ($runningProc) {
    Write-Warning "[SIONYX] AeroAdmin.exe is currently running (stuck hidden-window session?) - stopping it before staging."
    $runningProc | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

# 2) קובץ קיים אבל קטן/פגום (הורדה שנקטעה) - כמו ב-TeamViewer, "Test-Path" בלבד
#    לא מספיק כי קובץ פגום נשאר לנצח בלי שאף אחד יבחין, ואז AeroAdminSetupService
#    פשוט נכשל בשקט בכל ניסיון להפעיל אותו.
if (Test-Path $ExePath) {
    $existingSize = (Get-Item $ExePath).Length
    if ($existingSize -lt $MinValidSize) {
        Write-Warning "[SIONYX] Existing AeroAdmin.exe looks corrupt/truncated ($existingSize bytes) - deleting and re-downloading."
        Remove-Item -Path $ExePath -Force -ErrorAction SilentlyContinue
    }
}

if (Test-Path $ExePath) {
    Write-Host "[SIONYX] AeroAdmin.exe already staged and valid - skipping download."
} else {
    Write-Host "[SIONYX] Downloading AeroAdmin.exe..."
    Invoke-WebRequest -Uri $DownloadUrl -OutFile $ExePath

    $downloadedSize = (Get-Item $ExePath).Length
    if ($downloadedSize -lt $MinValidSize) {
        Write-Warning "[SIONYX] Downloaded AeroAdmin.exe looks too small ($downloadedSize bytes) - likely blocked/intercepted by a network filter. Leaving the file in place; AeroAdminSetupService's periodic retry (added earlier) will keep trying rather than fail permanently."
    }
}

Write-Host "[SIONYX] AeroAdmin staged at: $ExePath"
Write-Host "[SIONYX] One-time access-rights setup + ID readout is handled by the app itself (AeroAdminSetupService), not this script."
