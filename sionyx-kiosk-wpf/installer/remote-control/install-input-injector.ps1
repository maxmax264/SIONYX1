# install-input-injector.ps1
#
# Installs SionyxInputInjector as a LocalSystem Windows service. This
# exists to inject mouse clicks into UI that ignores input from a normal
# (Medium-integrity) process - see
# src\SionyxInputInjector\README.md for the full story and, importantly,
# the list of things about this that have NOT yet been verified on real
# hardware.
#
# Runs as an MSI CustomAction (Execute="deferred", Impersonate="no", i.e.
# as SYSTEM during install) - same pattern as install-tightvnc.ps1.
#
# NOT YET WIRED into Package.wxs's InstallExecuteSequence on purpose - see
# the README's rollout checklist. Once that checklist is done, add:
#   <Custom Action="CA_InstallInputInjector" After="CA_InstallTightVnc" Condition="NOT REMOVE" />
# alongside the CA_InstallInputInjector CustomAction definition already
# added to Package.wxs.

$ErrorActionPreference = 'Stop'

$ServiceName = 'SionyxInputInjector'
$InstallDir  = "${env:ProgramFiles}\SIONYX\InputInjector"
$ExeName     = 'SionyxInputInjector.exe'
$ExePath     = Join-Path $InstallDir $ExeName

# The published output is expected alongside this script (staged by
# build.ps1's publish step, same idea as how the main SionyxKiosk.exe
# publish output is staged for PublishFiles.wxs to harvest) - see
# build.ps1's Invoke-Publish for where SionyxInputInjector's own
# `dotnet publish` output needs to land before this script runs.
$SourceDir = Join-Path $PSScriptRoot 'SionyxInputInjector'

Write-Host "[SIONYX] Installing SionyxInputInjector (SYSTEM service for elevated-click input injection)..."

if (-Not (Test-Path $SourceDir)) {
    Write-Host "[SIONYX] SionyxInputInjector publish output not found at $SourceDir - skipping (elevated-click feature will be unavailable on this install)."
    exit 0
}

if (-Not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
}

$existingService = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($existingService) {
    Write-Host "[SIONYX] $ServiceName already exists - stopping before file update."
    if ($existingService.Status -ne 'Stopped') {
        Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
        $existingService.WaitForStatus('Stopped', (New-TimeSpan -Seconds 10))
    }
}

Copy-Item -Path (Join-Path $SourceDir '*') -Destination $InstallDir -Recurse -Force

if (-Not (Test-Path $ExePath)) {
    Write-Host "[SIONYX] ERROR: $ExePath not found after copy - aborting service install."
    exit 1
}

if ($existingService) {
    Write-Host "[SIONYX] Starting existing $ServiceName service."
    Start-Service -Name $ServiceName
} else {
    Write-Host "[SIONYX] Creating $ServiceName service (LocalSystem, auto-start)."
    # sc.exe (not New-Service) so we control the exact binPath quoting -
    # New-Service mangles paths with spaces in some PowerShell versions.
    $scArgs = @('create', $ServiceName, "binPath=`"$ExePath`"", 'start=', 'auto', 'obj=', 'LocalSystem')
    $result = & sc.exe @scArgs
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[SIONYX] ERROR: sc.exe create failed: $result"
        exit 1
    }
    & sc.exe description $ServiceName "SIONYX: injects mouse clicks for the VNC-relay elevated-click feature (see docs)." | Out-Null
    Start-Service -Name $ServiceName
}

Write-Host "[SIONYX] SionyxInputInjector installed and running."
