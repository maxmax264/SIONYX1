# install-anydesk.ps1
# מתקין AnyDesk כשירות רקע קבוע עם סיסמה ייחודית-אקראית, כתוכנת שליטה מרחוק שנייה ועצמאית
# המיועדת אך ורק לגישת המסטר (owner) - נפרדת לגמרי מ-RustDesk (שמיועד לארגון/מנהל).
# שתי התוכנות רצות זו לצד זו על אותו קיוסק, כל אחת עם הסיסמה שלה - אין תלות ביניהן.
#
# רץ בתוך ה-MSI (CustomAction), לא מתוך build.ps1.
# הפלט (AnyDesk ID + Password) נכתב ל-C:\ProgramData\SIONYX\anydesk-info.txt

$ErrorActionPreference = 'Stop'

$InstallDir  = "$env:ProgramFiles(x86)\AnyDesk"
$TempDir     = "C:\Temp"
$InfoDir     = "C:\ProgramData\SIONYX"
$InfoFile    = "$InfoDir\anydesk-info.txt"
$DownloadUrl = "https://download.anydesk.com/AnyDesk.exe"

Write-Host "[SIONYX] Installing AnyDesk (master-only remote-control agent)..."

if (-Not (Test-Path $TempDir)) { New-Item -ItemType Directory -Force -Path $TempDir | Out-Null }
if (-Not (Test-Path $InfoDir)) { New-Item -ItemType Directory -Force -Path $InfoDir | Out-Null }

$alreadyInstalled = $false
$existingService = Get-Service -Name "AnyDesk" -ErrorAction SilentlyContinue
if ($existingService -ne $null -and $existingService.Status -eq 'Running') {
    Write-Host "[SIONYX] AnyDesk already installed and running - skipping binary install."
    $alreadyInstalled = $true
}

if (-Not $alreadyInstalled) {
    Write-Host "[SIONYX] Downloading AnyDesk..."
    $ExePath = "$TempDir\AnyDesk.exe"
    Invoke-WebRequest -Uri $DownloadUrl -OutFile $ExePath

    # התקנה שקטה כשירות (unattended access)
    Write-Host "[SIONYX] Running silent install..."
    Start-Process -FilePath $ExePath -ArgumentList "--install `"$InstallDir`" --start-with-win --silent" -Wait
    Start-Sleep -Seconds 10

    $svc = Get-Service -Name "AnyDesk" -ErrorAction SilentlyContinue
    $tries = 0
    while (($svc -eq $null -or $svc.Status -ne 'Running') -and $tries -lt 10) {
        Start-Sleep -Seconds 3
        $svc = Get-Service -Name "AnyDesk" -ErrorAction SilentlyContinue
        $tries++
    }
}

Push-Location $InstallDir
$AnyDeskId = (.\AnyDesk.exe --get-id | Out-String).Trim()

if (Test-Path $InfoFile) {
    Write-Host "[SIONYX] anydesk-info.txt already exists - keeping existing password (update, not first install)."
    $existingContent = Get-Content $InfoFile -Raw
    if ($existingContent -match 'AnyDesk Password:\s*(\S+)') {
        $AnyDeskPassword = $matches[1]
    } else {
        $AnyDeskPassword = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 16 | ForEach-Object {[char]$_})
    }
} else {
    $AnyDeskPassword = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 16 | ForEach-Object {[char]$_})
}

# הגדרת סיסמה קבועה - AnyDesk קורא אותה מ-stdin (אין ארגומנט CLI ישיר לטקסט גלוי)
$AnyDeskPassword | .\AnyDesk.exe --set-password
Pop-Location

$info = @"
AnyDesk ID:       $AnyDeskId
AnyDesk Password: $AnyDeskPassword
Installed at:     $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Hostname:         $env:COMPUTERNAME
"@
Set-Content -Path $InfoFile -Value $info -Encoding UTF8

Write-Host "[SIONYX] AnyDesk installed. ID: $AnyDeskId"
Write-Host "[SIONYX] Details saved to: $InfoFile"
