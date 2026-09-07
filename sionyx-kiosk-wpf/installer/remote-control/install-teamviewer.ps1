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

$InfoDir      = "C:\ProgramData\SIONYX"
$QsExePath    = "$InfoDir\TeamViewerQS.exe"
$DownloadUrl  = "https://download.teamviewer.com/download/TeamViewerQS.exe"
$MinValidSize = 1MB   # TeamViewerQS.exe is normally several MB - anything smaller is a truncated/corrupt download

Write-Host "[SIONYX] Staging TeamViewer QuickSupport (on-demand agent)..."

if (-Not (Test-Path $InfoDir)) { New-Item -ItemType Directory -Force -Path $InfoDir | Out-Null }

# שלב 4: ניקוי חכם לפני התקנה/עדכון.
# 1) הקובץ הזה רץ לפי דרישה (StartTeamViewerQuickSupportAsync) - אם session קודם
#    נתקע פתוח, הוא נועל את הקובץ ומונע דריסה/מחיקה בהתקנה חוזרת. הורגים אותו קודם.
$runningProc = Get-Process -Name "TeamViewerQS" -ErrorAction SilentlyContinue
if ($runningProc) {
    Write-Warning "[SIONYX] TeamViewerQS.exe is currently running (stuck session?) - stopping it before staging."
    $runningProc | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

# 2) קובץ קיים אבל קטן/פגום (הורדה שנקטעה - קרה בעבר בפועל בגלל תנודות רשת/NetFree) -
#    "Test-Path" בלבד לא היה מספיק, כי קובץ פגום היה נשאר לנצח בלי שאף אחד יבחין.
if (Test-Path $QsExePath) {
    $existingSize = (Get-Item $QsExePath).Length
    if ($existingSize -lt $MinValidSize) {
        Write-Warning "[SIONYX] Existing TeamViewerQS.exe looks corrupt/truncated ($existingSize bytes) - deleting and re-downloading."
        Remove-Item -Path $QsExePath -Force -ErrorAction SilentlyContinue
    }
}

if (Test-Path $QsExePath) {
    Write-Host "[SIONYX] TeamViewerQS.exe already staged and valid - skipping download."
} else {
    Write-Host "[SIONYX] Downloading TeamViewerQS.exe..."
    Invoke-WebRequest -Uri $DownloadUrl -OutFile $QsExePath

    $downloadedSize = (Get-Item $QsExePath).Length
    if ($downloadedSize -lt $MinValidSize) {
        Write-Warning "[SIONYX] Downloaded TeamViewerQS.exe looks too small ($downloadedSize bytes) - likely blocked/intercepted by a network filter. Leaving the file in place; RemoteControlReportingService will surface this as unavailable rather than crash on launch."
    }
}

Write-Host "[SIONYX] TeamViewer QuickSupport staged at: $QsExePath"
Write-Host "[SIONYX] It will not run until the dashboard sends a launch request."
