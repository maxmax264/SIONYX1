content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\OrganizationMetadataService.cs', encoding='utf-8').read()
old = 'var result = await Firebase.DbGetAsync("metadata/settings/adminExitPassword");'
new = 'var result = await Firebase.DbGetPublicAsync("metadata/settings/adminExitPassword");'
print(content.count(old))
if content.count(old) == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\OrganizationMetadataService.cs', 'w', encoding='utf-8').write(content)
    print('OK')
