content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\SionyxKiosk.csproj', encoding='utf-8').read()
old = '    <TargetFramework>net8.0-windows</TargetFramework>'
new = '    <TargetFramework>net8.0-windows</TargetFramework>\n    <UseWindowsForms>true</UseWindowsForms>'
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\SionyxKiosk.csproj', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
