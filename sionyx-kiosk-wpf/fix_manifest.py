content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\SionyxKiosk.csproj', encoding='utf-8').read()
old = '<PropertyGroup>'
new = '<PropertyGroup>\n    <ApplicationManifest>app.manifest</ApplicationManifest>'
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\SionyxKiosk.csproj', 'w', encoding='utf-8').write(content)
    print('OK')
