content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\OrganizationMetadataService.cs', encoding='utf-8').read()
old = '''    public async Task<ServiceResult> GetAdminExitPasswordAsync()
    {
        try
        {
            var result = await Firebase.DbGetAsync("metadata/settings/adminExitPassword");'''
new = '''    public async Task<ServiceResult> GetAdminExitPasswordAsync()
    {
        try
        {
            var result = await Firebase.DbGetPublicAsync("metadata/settings/adminExitPassword");'''
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\OrganizationMetadataService.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
