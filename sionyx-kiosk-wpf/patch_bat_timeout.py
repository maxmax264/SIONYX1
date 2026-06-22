path = r"installer\CustomActions\KioskSetupActions.cs"

with open(path, "rb") as f:
    content = f.read().decode("utf-8")

old = '    taskkill /f /im SionyxKiosk.exe 2>nul\r\r\n    timeout /t 2 /nobreak >nul\r\r\n    msiexec /i ""%MSI_PATH%"" /quiet /norestart'
new = '    taskkill /f /im SionyxKiosk.exe 2>nul\r\r\n    timeout /t 8 /nobreak >nul\r\r\n    taskkill /f /im SionyxKiosk.exe 2>nul\r\r\n    timeout /t 3 /nobreak >nul\r\r\n    msiexec /i ""%MSI_PATH%"" /quiet /norestart'

if old in content:
    content = content.replace(old, new, 1)
    with open(path, "wb") as f:
        f.write(content.encode("utf-8"))
    print("Patched successfully!")
else:
    print("ERROR: not found")
