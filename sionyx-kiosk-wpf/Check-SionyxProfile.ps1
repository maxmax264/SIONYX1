# Check-SionyxProfile.ps1
param([string]$LogFile = "C:\Users\user\Desktop\sionyx_profile_check.log")
$ErrorActionPreference = "SilentlyContinue"
$results = @()
$allOk = $true
function Write-Log { param([string]$msg); $line = "[$(Get-Date -Format 'HH:mm:ss')] $msg"; Write-Host $line; Add-Content -Path $LogFile -Value $line -Encoding UTF8 }
function Add-Result { param([string]$label,[bool]$ok,[string]$detail); $icon = if ($ok) {"OK "} else {"ERR"}; $script:results += [PSCustomObject]@{Status=$icon;Label=$label;Detail=$detail}; if (-not $ok){$script:allOk=$false}; Write-Log "  [$icon] $label — $detail" }
if (Test-Path $LogFile){Remove-Item $LogFile -Force}
Write-Log "================================================================"
Write-Log " SIONYX Profile Diagnostic — $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Log "================================================================"
Write-Log "--- 1. User Account ---"
$userExists = (net user SionyxUser 2>&1) -notmatch "does not exist"
Add-Result "SionyxUser account exists" $userExists (if ($userExists){"OK"}else{"NOT FOUND"})
Write-Log "--- 2. SID ---"
try { $sid = (New-Object System.Security.Principal.NTAccount("SionyxUser")).Translate([System.Security.Principal.SecurityIdentifier]).Value; Add-Result "SID resolved" $true $sid } catch { Add-Result "SID resolved" $false "FAILED"; $sid=$null }
Write-Log "--- 3. ProfileList ---"
if ($sid) { $regPath="HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList\$sid"; $pk=Get-ItemProperty -Path $regPath 2>$null; $pke=($null -ne $pk); Add-Result "ProfileList key exists" $pke (if($pke){$regPath}else{"MISSING"}); if($pke){ $pip=$pk.ProfileImagePath; $pc=($pip -like "*SionyxUser*") -and ($pip -notlike "*TEMP*"); Add-Result "ProfileImagePath correct" $pc (if($pc){$pip}else{"BAD: $pip"}); $so=($pk.State -eq 0); Add-Result "State=0 (clean)" $so (if($so){"OK"}else{"State=0x$('{0:X}'-f $pk.State) CORRUPTED"}); $fp=($pk.FullProfile -eq 1); Add-Result "FullProfile=1" $fp (if($fp){"OK"}else{"FullProfile=$($pk.FullProfile)"}) } }
Write-Log "--- 4. Profile Folders ---"
$pp="C:\Users\SionyxUser"; $fe=Test-Path $pp; Add-Result "C:\Users\SionyxUser exists" $fe (if($fe){"OK"}else{"MISSING"})
if($fe){ @("Desktop","Documents","Downloads","Pictures","Music","Videos","AppData\Local","AppData\Local\Temp","AppData\LocalLow","AppData\Roaming") | ForEach-Object { $e=Test-Path (Join-Path $pp $_); Add-Result "Dir: $_" $e (if($e){"OK"}else{"MISSING"}) }; $nd=Test-Path "$pp\NTUSER.DAT"; Add-Result "NTUSER.DAT exists" $nd (if($nd){"OK"}else{"MISSING"}) }
Write-Log "--- 5. Leftover Folders ---"
$lo=Get-ChildItem "C:\Users"|Where-Object{$_.Name -like "SionyxUser.*" -or $_.Name -like "TEMP.*" -or $_.Name -eq "TEMP"}; $nlo=($lo.Count -eq 0); Add-Result "No leftover TEMP folders" $nlo (if($nlo){"Clean"}else{"FOUND: "+($lo.Name -join ", ")})
Write-Log "--- 6. AutoLogon ---"
$wl="HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"; $aa=(Get-ItemProperty $wl).AutoAdminLogon; Add-Result "AutoAdminLogon=0" ($aa -eq "0") (if($aa -eq "0"){"OK"}else{"VALUE=$aa STILL ON"}); $alc=(Get-ItemProperty $wl -Name AutoLogonCount 2>$null).AutoLogonCount; Add-Result "AutoLogonCount removed" ($null -eq $alc) (if($null -eq $alc){"OK"}else{"EXISTS=$alc"}); $dp=(Get-ItemProperty $wl -Name DefaultPassword 2>$null).DefaultPassword; Add-Result "DefaultPassword removed" ($null -eq $dp) (if($null -eq $dp){"OK"}else{"STILL EXISTS"})
Write-Log "--- 7. FirstLogonAnimation ---"
$fa=(Get-ItemProperty $wl -Name EnableFirstLogonAnimation 2>$null).EnableFirstLogonAnimation; Add-Result "EnableFirstLogonAnimation=1" ($fa -eq 1) (if($fa -eq 1){"OK"}else{"VALUE=$fa"})
Write-Log "--- 8. Scheduled Task ---"
schtasks /query /tn "SIONYX_FirstLogon" 2>&1|Out-Null; Add-Result "SIONYX_FirstLogon task removed" ($LASTEXITCODE -ne 0) (if($LASTEXITCODE -ne 0){"OK — gone"}else{"STILL EXISTS"})
Write-Log "--- 9. Active Sessions ---"
$sess=query session 2>&1|Select-String "SionyxUser"; $ns=($null -eq $sess -or $sess.Count -eq 0); Add-Result "No active SionyxUser sessions" $ns (if($ns){"OK"}else{"ACTIVE: "+($sess -join "; ")})
Write-Log "--- 10. Hive ---"
if($sid){ $hl=Test-Path "HKU:\$sid"; Add-Result "Hive not loaded in HKU" (-not $hl) (if(-not $hl){"OK"}else{"MOUNTED — cannot delete folders!"}) }
Write-Log ""; Write-Log "=== SUMMARY ==="; $err=$results|Where-Object{$_.Status -eq "ERR"}; Write-Log "Passed: $(($results|Where-Object{$_.Status -eq 'OK '}).Count) / $($results.Count)"; if($err.Count -gt 0){Write-Log "FAILED:"; $err|ForEach-Object{Write-Log "  [ERR] $($_.Label) — $($_.Detail)"}}; Write-Log (if($allOk){"RESULT: ALL OK"}else{"RESULT: PROBLEMS FOUND"}); Write-Log "Log: $LogFile"
$results|Format-Table -AutoSize
