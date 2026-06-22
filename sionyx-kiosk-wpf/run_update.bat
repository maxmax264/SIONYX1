@echo off
if exist "%TEMP%\pending_update.txt" (
    set /p MSI_PATH=<"%TEMP%\pending_update.txt"
    taskkill /f /im SionyxKiosk.exe 2>nul
    timeout /t 2 /nobreak >nul
    msiexec /i "%MSI_PATH%" /quiet /norestart
    del "%TEMP%\pending_update.txt"
    timeout /t 3 /nobreak >nul
    start "" "C:\Program Files\SIONYX\SionyxKiosk.exe"
)
