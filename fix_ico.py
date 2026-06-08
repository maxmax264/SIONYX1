content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\SionyxKiosk.csproj', encoding='utf-8').read()
old = '    <Content Include="Assets\\templates\\**" CopyToOutputDirectory="PreserveNewest" />'
new = '    <Content Include="Assets\\templates\\**" CopyToOutputDirectory="PreserveNewest" />\n    <Content Include="..\\..\\app-logo.ico" CopyToOutputDirectory="PreserveNewest" />'
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\SionyxKiosk.csproj', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
