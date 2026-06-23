content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\SystemServicesManager.cs', encoding='utf-8').read()

old1 = '        if (isKiosk)\n        {\n            _processRestriction.Start();\n            _keyboard.Start();\n        }'
new1 = '        if (isKiosk)\n        {\n            KioskPolicyService.Apply();\n            _processRestriction.Start();\n            _keyboard.Start();\n        }'

old2 = '            _processRestriction.Stop();\n            _keyboard.Stop();\n            _printMonitor.StopMonitoring();'
new2 = '            _processRestriction.Stop();\n            _keyboard.Stop();\n            KioskPolicyService.Remove();\n            _printMonitor.StopMonitoring();'

c1 = content.count(old1)
c2 = content.count(old2)
print(f"old1 matches: {c1}")
print(f"old2 matches: {c2}")

if c1 == 1 and c2 == 1:
    content = content.replace(old1, new1).replace(old2, new2)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\SystemServicesManager.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    idx = content.find('isKiosk')
    print(repr(content[idx:idx+200]))
