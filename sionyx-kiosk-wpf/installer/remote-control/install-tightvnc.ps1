# install-tightvnc.ps1
# מתקין TightVNC Server (open source, GPL) כשירות רקע, מאזין רק על
# 127.0.0.1:5900 - לעולם לא חשוף ברשת המקומית של הקיוסק. הגישה היחידה
# אליו היא דרך VncRelayService (SIONYX) שמגשר החוצה מעל WebSocket ל-
# sionyx-vnc-relay, ולכן לא צריך את TightVNC לפתוח פורט ב-firewall בכלל.
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

$existingService = Get-Service -Name "tvnserver" -ErrorAction SilentlyContinue
if ($existingService -ne $null -and $existingService.Status -eq 'Running') {
    Write-Host "[SIONYX] TightVNC already installed and running - skipping binary install, keeping existing password."
    $alreadyInstalled = $true
} else {
    $alreadyInstalled = $false
}

# סיסמה קבועה - נשמרת בהתקנה חוזרת (update), נוצרת רק בהתקנה ראשונה,
# כדי ש-VncRelayService/TightVNC לא "יאבדו" גישה בכל עדכון MSI.
if (Test-Path $InfoFile) {
    $existingContent = Get-Content $InfoFile -Raw
    if ($existingContent -match 'TightVNC Password:\s*(\S+)') {
        $VncPassword = $matches[1]
    } else {
        $VncPassword = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 16 | ForEach-Object {[char]$_})
    }
} else {
    $VncPassword = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 16 | ForEach-Object {[char]$_})
}

if (-Not $alreadyInstalled) {
    Write-Host "[SIONYX] Downloading TightVNC..."
    Invoke-WebRequest -Uri $MsiUrl -OutFile $MsiPath

    Write-Host "[SIONYX] Running silent install (server only, loopback-only listening, VNC auth)..."
    # ADDLOCAL=Server בלבד (בלי Viewer - אין צורך בו על הקיוסק).
    # ALLOWLOOPBACK רלוונטי רק להרשאות; ההגבלה ל-127.0.0.1 בפועל מתבצעת
    # ע"י LoopbackOnly ברישום למטה, כי אין property MSI ישיר לזה.
    $msiArgs = @(
        "/i", "`"$MsiPath`""
        "/quiet", "/norestart"
        "ADDLOCAL=Server"
        "SERVER_REGISTER_AS_SERVICE=1"
        "SERVER_ADD_FIREWALL_EXCEPTION=0"   # לא פותחים חריגת firewall - אין צורך, הגישה רק מקומית
        "SERVER_ALLOW_SAS=1"
        "SET_USEVNCAUTHENTICATION=1"
        "VALUE_OF_USEVNCAUTHENTICATION=1"
        "SET_PASSWORD=1"
        "VALUE_OF_PASSWORD=$VncPassword"
    )
    Start-Process -FilePath "msiexec.exe" -ArgumentList $msiArgs -Wait

    Start-Sleep -Seconds 5
    $svc = Get-Service -Name "tvnserver" -ErrorAction SilentlyContinue
    $tries = 0
    while (($svc -eq $null -or $svc.Status -ne 'Running') -and $tries -lt 10) {
        Start-Sleep -Seconds 3
        $svc = Get-Service -Name "tvnserver" -ErrorAction SilentlyContinue
        $tries++
    }
}

# הגבלה ל-loopback בלבד ברישום, כדי ש-tvnserver לא יאזין על שום ממשק
# רשת פיזי - היחיד שיכול להגיע ל-5900 הוא VncRelayService על אותו מחשב.
try {
    $regPath = "HKLM:\SOFTWARE\TightVNC\Server"
    if (Test-Path $regPath) {
        Set-ItemProperty -Path $regPath -Name "LoopbackOnly" -Value 1 -Type DWord -ErrorAction SilentlyContinue
        Restart-Service -Name "tvnserver" -Force -ErrorAction SilentlyContinue
    }
} catch {
    Write-Warning "[SIONYX] Could not set LoopbackOnly registry value (non-fatal, service may still be reachable only via 127.0.0.1 by default): $_"
}

$info = @"
TightVNC Password: $VncPassword
Installed at:       $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Hostname:            $env:COMPUTERNAME
Listens on:          127.0.0.1:5900 (loopback only - not reachable from the network)
"@
Set-Content -Path $InfoFile -Value $info -Encoding UTF8

Write-Host "[SIONYX] TightVNC installed and listening on 127.0.0.1:5900."
Write-Host "[SIONYX] Details saved to: $InfoFile"
