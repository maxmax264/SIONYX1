content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\OrganizationMetadataService.cs', encoding='utf-8').read()
idx = content.find('GetAdminExitPasswordAsync')
print(repr(content[idx-10:idx+500]))
