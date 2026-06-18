path = r'.\installer\Package.wxs'
content = open(path, encoding='utf-8').read()

old = '''  <InstallUISequence>
    <Custom Action="CA_LaunchKiosk" After="ExecuteAction" Condition="NOT REMOVE" />
  </InstallUISequence>'''

new = '''  <InstallExecuteSequence>
    <Custom Action="CA_LaunchKiosk" After="CA_VerifyInstallation" Condition="NOT REMOVE" />
  </InstallExecuteSequence>'''

# שים לב - יש כבר InstallExecuteSequence אחד, אז נוסיף שורה בתוכו במקום ליצור בלוק חדש
old2 = '      <Custom Action="CA_VerifyInstallation" After="WriteRegistryValues"  Condition="NOT REMOVE" />'
new2 = '      <Custom Action="CA_VerifyInstallation" After="WriteRegistryValues"  Condition="NOT REMOVE" />\n      <Custom Action="CA_LaunchKiosk"        After="CA_VerifyInstallation"  Condition="NOT REMOVE" />'

old3 = '''  <InstallUISequence>
    <Custom Action="CA_LaunchKiosk" After="ExecuteAction" Condition="NOT REMOVE" />
  </InstallUISequence>'''

count2 = content.count(old2)
count3 = content.count(old3)
print(f"VerifyInstallation line: {count2} matches")
print(f"InstallUISequence block: {count3} matches")

if count2 == 1 and count3 == 1:
    content = content.replace(old2, new2, 1)
    content = content.replace(old3, '', 1)
    open(path, 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
