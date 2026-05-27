lines = open(r'.\src\SionyxKiosk\Services\SystemServicesManager.cs', encoding='utf-8').readlines()

# מצא שורה 75 והוסף PreloadPricingAsync אחריה
idx = next(i for i,l in enumerate(lines) if '_ = _operatingHours.LoadSettingsAsync' in l)
lines.insert(idx + 1, '        _ = _printMonitor.PreloadPricingAsync();\n')

open(r'.\src\SionyxKiosk\Services\SystemServicesManager.cs', 'w', encoding='utf-8').writelines(lines)
print('OK')
