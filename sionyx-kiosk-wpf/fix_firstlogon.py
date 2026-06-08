content = open(r'.\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8').read()

old = '''                    key.SetValue("AutoLogonCount", 1, RegistryValueKind.DWord);'''

new = '''                    key.SetValue("AutoLogonCount", 1, RegistryValueKind.DWord);
                    key.SetValue("EnableFirstLogonAnimation", 1, RegistryValueKind.DWord);'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\installer\CustomActions\KioskSetupActions.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
