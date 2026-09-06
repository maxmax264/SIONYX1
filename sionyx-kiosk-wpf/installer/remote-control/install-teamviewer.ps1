# install-teamviewer.ps1
# מתקין TeamViewer Host כשירות רקע קבוע, עם סיסמה קבועה אחידה לכל הצי (לא רנדומלית
# per-machine כמו AnyDesk/RustDesk - הסיסמה מוצפנת בתוך teamviewer-unattended.reg
# ואין דרך לשנות אותה מבחוץ בלי לפצח את ההצפנה של TeamViewer). ה-ID כן ייחודי אוטומטית
# לכל מחשב. שימוש: לרשתות עם NetFree חוסם (המיירט AnyDesk), אחרי שאומת ש-TeamViewer
# עצמו לא מיורט (Windows כבר סומך על ה-CA שהרשת מזריקה - זה שונה מ-AnyDesk שעושה
# certificate pinning קשיח משלו).
#
# תלוי בקובץ teamviewer-unattended.reg שנוצר פעם אחת ידנית (Extras > Options >
# Advanced > Export configuration אחרי הגדרת Personal Password ב-GUI) ומאוחסן
# לצד הסקריפט הזה - TODO: עדיין לא סופק, הסקריפט ייכשל בלי זה.
#
# רץ בתוך ה-MSI (CustomAction), לא מתוך build.ps1.
# הפלט (TeamViewer ID + הסיסמה הקבועה הידועה) נכתב ל-C:\ProgramData\SIONYX\teamviewer-info.txt

$ErrorActionPreference = 'Stop'

$TempDir     = "C:\Temp"
$InfoDir     = "C:\ProgramData\SIONYX"
$InfoFile    = "$InfoDir\teamviewer-info.txt"
$DownloadUrl = "https://download.teamviewer.com/download/TeamViewer_Host.msi"
$RegFile     = Join-Path $PSScriptRoot "teamviewer-unattended.reg"

# TODO: להחליף בסיסמה הקבועה בפועל שהוגדרה כשה-.reg יוצא (רק לצורך כתיבתה ל-info
# file/Firebase - היא לא נשלחת בשום שלב בפועל אל TeamViewer, היא כבר מוטבעת ב-.reg)
$FixedPassword = "REPLACE_WITH_ACTUAL_FIXED_PASSWORD"

Write-Host "[SIONYX] Installing TeamViewer Host (fixed-password fleet agent)..."

if (-Not (Test-Path $TempDir)) { New-Item -ItemType Directory -Force -Path $TempDir | Out-Null }
if (-Not (Test-Path $InfoDir)) { New-Item -ItemType Directory -Force -Path $InfoDir | Out-Null }

if (-Not (Test-Path $RegFile)) {
    Write-Warning "[SIONYX] teamviewer-unattended.reg not found next to this script - aborting TeamViewer install. See install-teamviewer.ps1 header for how to generate it."
    exit 0
}

$alreadyInstalled = $false
$existingService = Get-Service -Name "TeamViewer" -ErrorAction SilentlyContinue
if ($existingService -ne $null -and $existingService.Status -eq 'Running') {
    Write-Host "[SIONYX] TeamViewer already installed and running - skipping binary install."
    $alreadyInstalled = $true
}

if (-Not $alreadyInstalled) {
    Write-Host "[SIONYX] Downloading TeamViewer Host MSI..."
    $MsiPath = "$TempDir\TeamViewer_Host.msi"
    Invoke-WebRequest -Uri $DownloadUrl -OutFile $MsiPath

    # IMPORTREGFILE - פרמטר MSI רשמי ומתועד, לא דורש רישיון Corporate/API token
    # (בניגוד ל-CUSTOMCONFIGID/APITOKEN שכן דורשים). מייבא את הגדרות ה-unattended
    # access + הסיסמה הקבועה שהוגדרו מראש ב-.reg, בלי כל אינטראקציה.
    Write-Host "[SIONYX] Running silent MSI install with IMPORTREGFILE..."
    $msiArgs = "/i `"$MsiPath`" /qn IMPORTREGFILE=`"$RegFile`" DESKTOPSHORTCUTS=0"
    Start-Process -FilePath "msiexec.exe" -ArgumentList $msiArgs -Wait
    Start-Sleep -Seconds 10

    $svc = Get-Service -Name "TeamViewer" -ErrorAction SilentlyContinue
    $tries = 0
    while (($svc -eq $null -or $svc.Status -ne 'Running') -and $tries -lt 10) {
        Start-Sleep -Seconds 3
        $svc = Get-Service -Name "TeamViewer" -ErrorAction SilentlyContinue
        $tries++
    }
}

# ה-ClientID נכתב לרישום מיד עם עליית השירות, אבל יכול לקחת רגע - כמו ב-AnyDesk,
# מנסים כמה פעמים לפני שמוותרים.
$TeamViewerId = $null
$idTries = 0
while ([string]::IsNullOrWhiteSpace($TeamViewerId) -and $idTries -lt 10) {
    $TeamViewerId = (Get-ItemProperty "HKLM:\SOFTWARE\WOW6432Node\TeamViewer" -Name ClientID -ErrorAction SilentlyContinue).ClientID
    if ([string]::IsNullOrWhiteSpace($TeamViewerId)) {
        Start-Sleep -Seconds 3
        $idTries++
    }
}
if ([string]::IsNullOrWhiteSpace($TeamViewerId)) {
    Write-Warning "[SIONYX] TeamViewer ClientID still empty after $idTries retries - will retry again on next app start via RemoteControlReportingService."
    $TeamViewerId = ''
}

$info = @"
TeamViewer ID:       $TeamViewerId
TeamViewer Password: $FixedPassword
Installed at:        $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Hostname:            $env:COMPUTERNAME
"@
Set-Content -Path $InfoFile -Value $info -Encoding UTF8

Write-Host "[SIONYX] TeamViewer installed. ID: $TeamViewerId"
Write-Host "[SIONYX] Details saved to: $InfoFile"
