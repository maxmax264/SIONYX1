import re
for fname in [r'.\src\SionyxKiosk\Services\PrintMonitorService.cs',
              r'.\src\SionyxKiosk\Services\SessionService.cs']:
    c = open(fname, encoding='utf-8').read()
    c = c.replace('$"users/{_userId}/printBalance"', '$"users/{_userId}/printBalance"'.replace('users/', f'organizations/{{_orgId}}/users/') if '_orgId' in c else c)
    open(fname, 'w', encoding='utf-8').write(c)
    print(fname, 'done')
