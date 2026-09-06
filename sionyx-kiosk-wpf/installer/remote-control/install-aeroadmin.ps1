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

$InfoDir     = "C:\ProgramData\SIONYX"
$ExePath     = "$InfoDir\AeroAdmin.exe"
$DownloadUrl = "https://ulm.aeroadmin.com/AeroAdmin.exe"

Write-Host "[SIONYX] Staging AeroAdmin (portable, on-demand agent)..."

if (-Not (Test-Path $InfoDir)) { New-Item -ItemType Directory -Force -Path $InfoDir | Out-Null }

if (Test-Path $ExePath) {
    Write-Host "[SIONYX] AeroAdmin.exe already staged - skipping download."
} else {
    Write-Host "[SIONYX] Downloading AeroAdmin.exe..."
    Invoke-WebRequest -Uri $DownloadUrl -OutFile $ExePath
}

Write-Host "[SIONYX] AeroAdmin staged at: $ExePath"
Write-Host "[SIONYX] One-time access-rights setup + ID readout is handled by the app itself (AeroAdminSetupService), not this script."
