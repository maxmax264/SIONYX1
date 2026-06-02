content = open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\Services\OrganizationMetadataService.cs', encoding='utf-8').read()

old = '            var enabled = enabledJson.Trim() == "true";'
new = '            var enabled = enabledJson.Trim().ToLower() == "true";'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\Services\OrganizationMetadataService.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
