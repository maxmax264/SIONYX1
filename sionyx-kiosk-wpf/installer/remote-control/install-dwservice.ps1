# install-dwservice.ps1
# מתקין DWAgent (DWService) כסוכן שליטה מרחוק שלישי, גיבוי ל-RustDesk/AnyDesk.
# בניגוד לשניים האלה - DWService לא מייצר ID+סיסמה מקומיים; המכשיר מצטרף ישירות
# לחשבון DWService שלכם (כמו TeamViewer, אבל בחינם לגמרי, ללא חסימת "שימוש עסקי"
# וללא צורך בחשבון בתשלום). אחרי ההתקנה המחשב פשוט מופיע ברשימת המכשירים בחשבון.
#
# חינמי + קוד פתוח + ללא הגבלת מספר מכשירים (יש הגבלת bandwidth ~6Mbps בטיר החינמי -
# מספיק לגישת ניהול/תמיכה, לא ל-streaming כבד).
#
# רץ בתוך ה-MSI (CustomAction), לא מתוך build.ps1.
# $env:DWSERVICE_USER / $env:DWSERVICE_INSTALL_PASSWORD מגיעים מ-build.ps1 (לא מוטבעים
# בקוד/git) ומועברים כארגומנטים דרך משתני WiX preprocessor - ראו Package.wxs.
#
# "InstallPassword" הוא לא סיסמת ההתחברות לחשבון - זו "Agent installation password"
# נפרדת שמוגדרת פעם אחת בהגדרות החשבון ב-DWService (מטעמי אבטחה, כדי לא להטביע את
# סיסמת הכניסה בפועל בתוך קבצי ה-MSI המופצים).

param(
    [Parameter(Mandatory = $true)][string]$User,
    [Parameter(Mandatory = $true)][string]$InstallPassword
)

$ErrorActionPreference = 'Stop'

$InstallDir = "$env:ProgramFiles\DWAgent"
$TempDir    = "C:\Temp"
$InfoDir    = "C:\ProgramData\SIONYX"
$LogFile    = "$InfoDir\dwagent-install.log"

# ⚠️ קישור ההורדה הזה לא אומת אוטומטית (עמוד ההורדה של DWService דורש אישור תנאים
# בדפדפן ולא חשף קישור ישיר קבוע בזמן הכתיבה). לפני ריצה ראשונה: לכו ל-
# https://www.dwservice.net/en/download.html -> Agent -> Windows, קליק ימני על כפתור
# ה-Download -> Copy Link, והדביקו כאן במקום השורה הבאה אם היא לא עובדת.
$DownloadUrl = "https://www.dwservice.net/download/dwagent.exe"

Write-Host "[SIONYX] Installing DWAgent (3rd backup remote-control agent)..."

if (-Not (Test-Path $TempDir)) { New-Item -ItemType Directory -Force -Path $TempDir | Out-Null }
if (-Not (Test-Path $InfoDir)) { New-Item -ItemType Directory -Force -Path $InfoDir | Out-Null }

$alreadyInstalled = $false
if (Test-Path "$InstallDir\dwagent.exe") {
    Write-Host "[SIONYX] DWAgent already installed - skipping binary install."
    $alreadyInstalled = $true
}

if (-Not $alreadyInstalled) {
    Write-Host "[SIONYX] Downloading DWAgent..."
    $ExePath = "$TempDir\dwagent.exe"
    Invoke-WebRequest -Uri $DownloadUrl -OutFile $ExePath

    Write-Host "[SIONYX] Running silent install (joins the SIONYX DWService account)..."
    # user/password = חשבון DWService; name = שם המכשיר ברשימה; group = קיבוץ בחשבון;
    # logpath = לצורך דיבאג אם ההתקנה נכשלת.
    $installArgs = "-silent user=$User password=$InstallPassword name=$env:COMPUTERNAME group=SIONYX logpath=$LogFile"
    Start-Process -FilePath $ExePath -ArgumentList $installArgs -Wait
    Start-Sleep -Seconds 10
}

if (Test-Path "$InstallDir\dwagent.exe") {
    Write-Host "[SIONYX] DWAgent installed successfully - device should appear in the DWService account shortly."
} else {
    Write-Warning "[SIONYX] DWAgent install may have failed - check $LogFile"
}
