content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\SionyxKiosk.csproj', encoding='utf-8').read()
old = '    <UseWindowsForms>true</UseWindowsForms>\n'
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, '', 1)
    old2 = '    <PackageReference Include="Serilog.Sinks.File" Version="7.0.0" />'
    new2 = '    <PackageReference Include="Serilog.Sinks.File" Version="7.0.0" />\n    <PackageReference Include="Hardcodet.NotifyIcon.Wpf" Version="1.1.0" />'
    content = content.replace(old2, new2, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\SionyxKiosk.csproj', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
