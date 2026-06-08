content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\SionyxKiosk.csproj', encoding='utf-8').read()
old = '    <TargetFramework>net8.0-windows</TargetFramework>\n    <UseWindowsForms>true</UseWindowsForms>'
new = '    <TargetFramework>net8.0-windows</TargetFramework>'
count = content.count(old)
print(f"patch1: {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    print("patch1 OK")
else:
    print("patch1 NOT FOUND")
    exit(1)

old2 = '  </ItemGroup>\n</Project>'
new2 = '    <FrameworkReference Include="Microsoft.WindowsDesktop.App.WindowsForms" />\n  </ItemGroup>\n</Project>'
count2 = content.count(old2)
print(f"patch2: {count2} matches")
if count2 == 1:
    content = content.replace(old2, new2, 1)
    print("patch2 OK")
else:
    print("patch2 NOT FOUND")
    exit(1)

open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\SionyxKiosk.csproj', 'w', encoding='utf-8').write(content)
print('DONE')
