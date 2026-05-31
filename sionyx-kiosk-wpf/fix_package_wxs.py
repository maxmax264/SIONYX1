content = open(r'.\installer\Package.wxs', encoding='utf-8').read()

old = '    <!-- Public property for Organization ID (set by custom dialog) -->\n    <Property Id="ORGID" Secure="yes" />'
new = '    <!-- Public property for Organization ID (set by custom dialog) -->\n    <Property Id="ORGID" Secure="yes" />\n    <!-- Public property for Computer Name (set by custom dialog) -->\n    <Property Id="COMPUTERNAME_CUSTOM" Secure="yes" />'

count = content.count(old)
print(f"Step 1: {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    print("Step 1: OK")
else:
    print("Step 1: NOT FOUND - stop"); exit()

old2 = '          <RegistryValue Name="OrgId"        Type="string" Value="[ORGID]" />\n          <RegistryValue Name="KioskUsername" Type="string" Value="SionyxUser" />'
new2 = '          <RegistryValue Name="OrgId"        Type="string" Value="[ORGID]" />\n          <RegistryValue Name="ComputerName"  Type="string" Value="[COMPUTERNAME_CUSTOM]" />\n          <RegistryValue Name="KioskUsername" Type="string" Value="SionyxUser" />'

count2 = content.count(old2)
print(f"Step 2: {count2} matches")
if count2 == 1:
    content = content.replace(old2, new2, 1)
    open(r'.\installer\Package.wxs', 'w', encoding='utf-8').write(content)
    print("Step 2: OK - file written")
else:
    print("Step 2: NOT FOUND - stop")
