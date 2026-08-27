# install-rustdesk.ps1
# מתקין RustDesk כשירות רקע קבוע עם סיסמה ייחודית-אקראית לכל מחשב, כחלק מהתקנת קיוסק SIONYX.
# רץ בתוך ה-MSI (CustomAction), לא מתוך build.ps1 (זה רץ על מחשב המפתח, לא על הקיוסק).
#
# הפלט (RustDesk ID + Password) נכתב ל-C:\ProgramData\SIONYX\rustdesk-info.txt
# ונקרא משם ע"י האפליקציה (RemoteControlReportingService) כדי לדווח ל-Firebase.
#
# חשוב: אין כאן סיסמה משותפת קבועה בקוד. כל מחשב מקבל סיסמה אקראית משלו בזמן ההתקנה.

$ErrorActionPreference = 'Stop'

$InstallDir  = "$env:ProgramFiles\RustDesk"
$TempDir     = "C:\Temp"
$InfoDir     = "C:\ProgramData\SIONYX"
$InfoFile    = "$InfoDir\rustdesk-info.txt"

Write-Host "[SIONYX] Installing RustDesk (org remote-control agent)..."

if (-Not (Test-Path $TempDir)) { New-Item -ItemType Directory -Force -Path $TempDir | Out-Null }
if (-Not (Test-Path $InfoDir)) { New-Item -ItemType Directory -Force -Path $InfoDir | Out-Null }

$alreadyInstalled = $false
$existingService = Get-Service -Name "Rustdesk" -ErrorAction SilentlyContinue
if ($existingService -ne $null -and $existingService.Status -eq 'Running') {
    Write-Host "[SIONYX] RustDesk already installed and running - skipping binary install."
    $alreadyInstalled = $true
}

if (-Not $alreadyInstalled) {
    # ---- מציאת קישור ההורדה העדכני ----
    Write-Host "[SIONYX] Resolving latest RustDesk release..."
    $Page = Invoke-WebRequest -Uri 'https://github.com/rustdesk/rustdesk/releases/latest' -UseBasicParsing
    $HTML = New-Object -Com "HTMLFile"
    try {
        $HTML.IHTMLDocument2_write($Page.Content)
    } catch {
        $src = [System.Text.Encoding]::Unicode.GetBytes($Page.Content)
        $HTML.write($src)
    }
    $DownloadLink = ($HTML.Links | Where-Object { $_.href -match '(.)+\/rustdesk\/rustdesk\/releases\/download\/\d{1}.\d{1,2}.\d{1,2}(.{0,3})\/rustdesk(.)+x86_64.exe' } | Select-Object -First 1).href
    $DownloadLink = $DownloadLink.Replace('about:', 'https://github.com')

    if ([string]::IsNullOrWhiteSpace($DownloadLink)) {
        throw "[SIONYX] Could not resolve RustDesk download link. Check network / GitHub availability."
    }

    Write-Host "[SIONYX] Downloading: $DownloadLink"
    $ExePath = "$TempDir\rustdesk.exe"
    Invoke-WebRequest -Uri $DownloadLink -OutFile $ExePath

    # ---- התקנה שקטה ----
    Write-Host "[SIONYX] Running silent install..."
    Start-Process -FilePath $ExePath -ArgumentList "--silent-install" -Wait
    Start-Sleep -Seconds 15

    # ---- התקנה כשירות (unattended access) ----
    Push-Location $InstallDir
    $svc = Get-Service -Name "Rustdesk" -ErrorAction SilentlyContinue
    if ($svc -eq $null) {
        Write-Host "[SIONYX] Installing as Windows service..."
        Start-Process -FilePath ".\rustdesk.exe" -ArgumentList "--install-service" -Wait
        Start-Sleep -Seconds 15
        $svc = Get-Service -Name "Rustdesk"
    }
    $tries = 0
    while ($svc.Status -ne 'Running' -and $tries -lt 10) {
        Start-Service "Rustdesk" -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 3
        $svc.Refresh()
        $tries++
    }
    Pop-Location
}

# ---- קביעת סיסמה ייחודית-אקראית לכל מחשב + קריאת ה-ID ----
# אם כבר קיים rustdesk-info.txt מהתקנה קודמת - לא מייצרים סיסמה חדשה (עדכון גרסה לא ישבור גישה קיימת).
Push-Location $InstallDir
$RustDeskId = (.\rustdesk.exe --get-id | Out-String).Trim()

if (Test-Path $InfoFile) {
    Write-Host "[SIONYX] rustdesk-info.txt already exists - keeping existing password (update, not first install)."
    $existingContent = Get-Content $InfoFile -Raw
    if ($existingContent -match 'RustDesk Password:\s*(\S+)') {
        $RustDeskPassword = $matches[1]
        .\rustdesk.exe --password $RustDeskPassword | Out-Null
    } else {
        # קובץ קיים אבל בפורמט לא צפוי - מייצרים סיסמה חדשה כגיבוי
        $RustDeskPassword = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 16 | ForEach-Object {[char]$_})
        .\rustdesk.exe --password $RustDeskPassword | Out-Null
    }
} else {
    # התקנה ראשונה - סיסמה אקראית ייחודית למחשב הזה בלבד
    $RustDeskPassword = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 16 | ForEach-Object {[char]$_})
    .\rustdesk.exe --password $RustDeskPassword | Out-Null
}
Pop-Location

# ---- תיעוד מקומי (נקרא ע"י האפליקציה כדי לדווח ל-Firebase) ----
$info = @"
RustDesk ID:       $RustDeskId
RustDesk Password: $RustDeskPassword
Installed at:      $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Hostname:          $env:COMPUTERNAME
"@
Set-Content -Path $InfoFile -Value $info -Encoding UTF8

Write-Host "[SIONYX] RustDesk installed. ID: $RustDeskId"
Write-Host "[SIONYX] Details saved to: $InfoFile"
