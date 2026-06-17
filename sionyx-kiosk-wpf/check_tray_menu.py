content = open(r'.\src\SionyxKiosk\Services\TrayIconService.cs', encoding='utf-8').read()
idx = content.find('settingsItem')
print(content[idx:idx+300])
