$key = Get-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer" -Name "NoControlPanel" -ErrorAction SilentlyContinue
if ($key) {
    Write-Host "NoControlPanel EXISTS, value =" $key.NoControlPanel
} else {
    Write-Host "NoControlPanel does NOT exist in registry"
}
