# install-tightvnc.ps1
# מתקין TightVNC Server (open source, GPL) שרץ **בתוך ה-session של המשתמש
# המחובר** (לא כשירות Windows!) - מאזין רק על 127.0.0.1:5900, לעולם לא
# חשוף ברשת המקומית של הקיוסק. הגישה היחידה אליו היא דרך VncRelayService
# (SIONYX) שמגשר החוצה מעל WebSocket ל-sionyx-vnc-relay.
#
# חשוב: TightVNC בהתקנה כשירות (Windows Service) רץ ב-Session 0, שהוא
# session נפרד מהדסקטופ האינטראקטיבי של המשתמש המחובר - לכן הוא תופס
# מסך שחור/ריק במקום מה שבאמת מוצג על הצג. הפתרון: לא רושמים אותו
# כשירות כלל; VncRelayService.cs מפעיל את tvnserver.exe ישירות (עם
# "-run") מתוך ה-session של הקיוסק בזמן שה-VncRelayService עצמו עולה,
# בדיוק כמו שהאפליקציה של הקיוסק עצמה רצה. כך tvnserver "רואה" את
# המסך האמיתי.
#
# למה TightVNC ולא RustDesk/AnyDesk לצורך הזה: TightVNC לא עושה שום
# הצפנה/סרטיפיקט משלו (RFB גולמי) - כל ה-TLS קורה ברמת ה-WebSocket של
# VncRelayService, שכבר מוכח עובד מול NetFree (אותו HttpClient שמדבר עם
# Firebase). אין כאן סרטיפיקט צרוב שיכול להיתקע כמו שקרה ל-RustDesk/AnyDesk.
#
# רץ בתוך ה-MSI (CustomAction), כמו install-anydesk.ps1.
# הפלט (סיסמה) נכתב ל-C:\ProgramData\SIONYX\tightvnc-info.txt

$ErrorActionPreference = 'Stop'

$InstallDir  = "${env:ProgramFiles}\TightVNC"
$TempDir     = "C:\Temp"
$InfoDir     = "C:\ProgramData\SIONYX"
$InfoFile    = "$InfoDir\tightvnc-info.txt"
$MsiUrl      = "https://www.tightvnc.com/download/2.8.88/tightvnc-2.8.88-gpl-setup-64bit.msi"
$MsiPath     = "$TempDir\tightvnc-setup.msi"

Write-Host "[SIONYX] Installing TightVNC (local-only VNC server for the VNC-relay remote-control feature)..."

if (-Not (Test-Path $TempDir)) { New-Item -ItemType Directory -Force -Path $TempDir | Out-Null }
if (-Not (Test-Path $InfoDir)) { New-Item -ItemType Directory -Force -Path $InfoDir | Out-Null }

$alreadyInstalled = Test-Path "$InstallDir\tvnserver.exe"
if ($alreadyInstalled) {
    Write-Host "[SIONYX] TightVNC binaries already installed - skipping MSI, keeping existing password."
}

# אין סיסמת VNC נפרדת בכוונה: הגישה היחידה ל-tvnserver היא מ-127.0.0.1
# (loopback בלבד, למטה) דרך VncRelayService, שכבר שומר על עצמו מאחורי
# ה-token החד-פעמי שהדשבורד מייצר. דרשנו בעבר גם VNC Authentication,
# אבל הדשבורד מעולם לא קיבל/העביר את הסיסמה הזו ל-viewer (novnc) - כל
# ניסיון חיבור נכשל עם "authentication failed" מיד אחרי החיבור
# (ה-"nc נפל" ב-vnc.html). במקום לשרשר עוד שכבת סוד שצריך להעביר,
# מבטלים את שכבת הסיסמה: היא לא הוסיפה הגנה אמיתית (loopback-only +
# token חד-פעמי כבר עושים את זה) ורק שברה את הזרימה.

if (-Not $alreadyInstalled) {
    Write-Host "[SIONYX] Downloading TightVNC..."
    Invoke-WebRequest -Uri $MsiUrl -OutFile $MsiPath

    Write-Host "[SIONYX] Running silent install (server only, loopback-only listening, no VNC auth, NOT as a Windows service)..."
    # ADDLOCAL=Server בלבד (בלי Viewer - אין צורך בו על הקיוסק).
    # SERVER_REGISTER_AS_SERVICE=0 בכוונה: שירות Windows רץ ב-Session 0
    # ותופס מסך שחור. tvnserver.exe מופעל בהמשך ישירות מתוך VncRelayService
    # (ב-SystemServicesManager), בתוך ה-session האינטראקטיבי של הקיוסק.
    $msiArgs = @(
        "/i", "`"$MsiPath`""
        "/quiet", "/norestart"
        "ADDLOCAL=Server"
        "SERVER_REGISTER_AS_SERVICE=0"
        "SERVER_ADD_FIREWALL_EXCEPTION=0"   # לא פותחים חריגת firewall - אין צורך, הגישה רק מקומית
        "SERVER_ALLOW_SAS=1"
        "SET_USEVNCAUTHENTICATION=1"
        "VALUE_OF_USEVNCAUTHENTICATION=0"
    )
    Start-Process -FilePath "msiexec.exe" -ArgumentList $msiArgs -Wait
}

# אם מהתקנה קודמת (לפני התיקון הזה) tvnserver כבר רשום כשירות Windows -
# מכבים אותו, כדי שלא יתחרה על פורט 5900 עם ה-session-mode instance
# ולא ימשיך לתפוס מסך שחור.
try {
    $existingService = Get-Service -Name "tvnserver" -ErrorAction SilentlyContinue
    if ($existingService -ne $null) {
        Write-Host "[SIONYX] Found tvnserver registered as a Windows service from a previous install - disabling it (session-mode only from now on)."
        Stop-Service -Name "tvnserver" -Force -ErrorAction SilentlyContinue
        Set-Service -Name "tvnserver" -StartupType Disabled -ErrorAction SilentlyContinue
    }
} catch {
    Write-Warning "[SIONYX] Could not disable a pre-existing tvnserver service (non-fatal): $_"
}

# הגבלה ל-loopback בלבד ברישום, כדי ש-tvnserver לא יאזין על שום ממשק
# רשת פיזי - היחיד שיכול להגיע ל-5900 הוא VncRelayService על אותו מחשב.
# (אותו מפתח רישום נקרא גם ע"י tvnserver.exe במצב session, לא רק שירות.)
try {
    $regPath = "HKLM:\SOFTWARE\TightVNC\Server"
    if (Test-Path $regPath) {
        Set-ItemProperty -Path $regPath -Name "LoopbackOnly" -Value 1 -Type DWord -ErrorAction SilentlyContinue
    }
} catch {
    Write-Warning "[SIONYX] Could not set LoopbackOnly registry value (non-fatal): $_"
}

# מכבים VNC Authentication ברישום גם על התקנות קיימות (לא רק MSI חדש) -
# כדי שקיוסקים שכבר קיבלו TightVNC עם הסיסמה הישנה יתוקנו בלי דרישה
# להסרה/התקנה מחדש. tvnserver קורא את זה מהרישום גם במצב session.
try {
    $regPath = "HKLM:\SOFTWARE\TightVNC\Server"
    if (Test-Path $regPath) {
        Set-ItemProperty -Path $regPath -Name "UseVncAuthentication" -Value 0 -Type DWord -ErrorAction SilentlyContinue
    }
} catch {
    Write-Warning "[SIONYX] Could not disable UseVncAuthentication registry value (non-fatal): $_"
}

# אם tvnserver כבר רץ (מותקן קודם), נהרוג אותו כדי ש-VncRelayService
# יפעיל אותו מחדש בפעם הבאה עם ההגדרה החדשה (tvnserver קורא את הרישום
# רק בעלייה, לא live).
try {
    $running = Get-Process -Name "tvnserver" -ErrorAction SilentlyContinue
    if ($running) {
        Write-Host "[SIONYX] Restarting tvnserver.exe so the auth-disabled setting takes effect..."
        Stop-Process -Name "tvnserver" -Force -ErrorAction SilentlyContinue
    }
} catch {
    Write-Warning "[SIONYX] Could not restart tvnserver.exe (non-fatal): $_"
}

$info = @"
Auth:                Disabled (loopback-only + one-time relay token is the access control)
Installed at:       $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Hostname:            $env:COMPUTERNAME
Mode:                Session (launched by VncRelayService, NOT a Windows service)
Listens on:          127.0.0.1:5900 (loopback only - not reachable from the network)
"@
Set-Content -Path $InfoFile -Value $info -Encoding UTF8

Write-Host "[SIONYX] TightVNC installed. It will start automatically in the kiosk's own session when VncRelayService runs."
Write-Host "[SIONYX] Details saved to: $InfoFile"

