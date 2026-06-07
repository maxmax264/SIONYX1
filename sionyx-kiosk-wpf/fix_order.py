content = open(r'.\installer\Package.wxs', encoding='utf-8').read()
old = '''      <Custom Action="CA_CreateKioskUser"          After="InstallFiles"                 Condition="NOT Installed AND NOT REMOVE" />
      <Custom Action="CA_ApplySecurityRestrictions" After="CA_CreateKioskUser"           Condition="NOT Installed AND NOT REMOVE" />
      <Custom Action="CA_SetupAutoStart"           After="CA_ApplySecurityRestrictions"  Condition="NOT Installed AND NOT REMOVE" />
      <Custom Action="CA_InitializeProfile"        After="CA_SetupAutoStart"            Condition="NOT Installed AND NOT REMOVE" />'''
new = '''      <Custom Action="CA_CreateKioskUser"          After="InstallFiles"                 Condition="NOT Installed AND NOT REMOVE" />
      <Custom Action="CA_InitializeProfile"        After="CA_CreateKioskUser"           Condition="NOT Installed AND NOT REMOVE" />
      <Custom Action="CA_ApplySecurityRestrictions" After="CA_InitializeProfile"         Condition="NOT Installed AND NOT REMOVE" />
      <Custom Action="CA_SetupAutoStart"           After="CA_ApplySecurityRestrictions"  Condition="NOT Installed AND NOT REMOVE" />'''
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\installer\Package.wxs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
