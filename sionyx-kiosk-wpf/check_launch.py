content = open(r'.\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8').read()
idx = content.find('LaunchKiosk')
print(repr(content[idx:idx+400]))
