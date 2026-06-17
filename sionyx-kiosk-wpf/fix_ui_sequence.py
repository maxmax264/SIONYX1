content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\Package.wxs', encoding='utf-8').read()

old = '</InstallExecuteSequence>'

new = '''</InstallExecuteSequence>

  <InstallUISequence>
    <Custom Action="CA_LaunchKiosk" After="ExecuteAction" Condition="NOT REMOVE" />
  </InstallUISequence>'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\Package.wxs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
