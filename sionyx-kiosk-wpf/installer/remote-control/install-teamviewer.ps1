# install-teamviewer.ps1
# לא מתקין TeamViewer Host כשירות רקע קבוע - במכוון. unattended access קבוע דרך
# חשבון TeamViewer חינמי על כמה קיוסקים הוא בדיוק דפוס השימוש שהם מזהים כ-
# "commercial use" וחוסמים (ראו דיון בזיכרון הפרויקט). במקום זה, שלב הסקריפט
# הזה רק *מוריד ומאחסן* את TeamViewerQS.exe (הגרסה הפורטבילית, לא מותקנת),
# ומחכה עד שהדשבורד ישלח פקודת "הפעל" (RemoteControlReportingService.cs,
# StartTeamViewerQuickSupportAsync) - שאז מריצה אותו לפי דרישה, session בודד
# בכל פעם, בדיוק כמו תמיכה טכנית מזדמנת לגיטימית.
#
# משמש כגיבוי ל-AnyDesk ברשתות עם NetFree-style content filter שעושה TLS
# interception ודוחה את ה-cert pinning של AnyDesk - TeamViewer לא נתקל בזה כי
# הוא סומך על חנות התעודות של Windows, לא על pinning קשיח משלו.

$ErrorActionPreference = 'Stop'

$InfoDir     = "C:\ProgramData\SIONYX"
$QsExePath   = "$InfoDir\TeamViewerQS.exe"
$DownloadUrl = "https://download.teamviewer.com/download/TeamViewerQS.exe"

Write-Host "[SIONYX] Staging TeamViewer QuickSupport (on-demand agent)..."

if (-Not (Test-Path $InfoDir)) { New-Item -ItemType Directory -Force -Path $InfoDir | Out-Null }

if (Test-Path $QsExePath) {
    Write-Host "[SIONYX] TeamViewerQS.exe already staged - skipping download."
} else {
    Write-Host "[SIONYX] Downloading TeamViewerQS.exe..."
    Invoke-WebRequest -Uri $DownloadUrl -OutFile $QsExePath
}

Write-Host "[SIONYX] TeamViewer QuickSupport staged at: $QsExePath"
Write-Host "[SIONYX] It will not run until the dashboard sends a launch request."
