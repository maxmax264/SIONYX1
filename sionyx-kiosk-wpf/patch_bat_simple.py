path = r"installer\CustomActions\KioskSetupActions.cs"

with open(path, "rb") as f:
    content = f.read().decode("utf-8")

# Find and replace the problematic loop with simple timeouts
old = '    taskkill /f /im SionyxKiosk.exe 2>nul\r\r\n    :waitloop\r\r\n    tasklist /fi "imagename eq SionyxKiosk.exe" 2>nul | find /i "SionyxKiosk.exe" >nul\r\r\n    if not errorlevel 1 (\r\r\n        timeout /t 2 /nobreak >nul\r\r\n        taskkill /f /im SionyxKiosk.exe 2>nul\r\r\n        goto waitloop\r\r\n    )\r\r\n    msiexec /i ""%MSI_PATH%"" /quiet /norestart'

new = '    taskkill /f /im SionyxKiosk.exe 2>nul\r\r\n    timeout /t 5 /nobreak >nul\r\r\n    taskkill /f /im SionyxKiosk.exe 2>nul\r\r\n    timeout /t 5 /nobreak >nul\r\r\n    msiexec /i ""%MSI_PATH%"" /quiet /norestart'

if old in content:
    content = content.replace(old, new, 1)
    with open(path, "wb") as f:
        f.write(content.encode("utf-8"))
    print("Patched successfully!")
else:
    print("ERROR: not found")
    idx = content.find(":waitloop")
    if idx != -1:
        print(repr(content[idx-50:idx+200]))
