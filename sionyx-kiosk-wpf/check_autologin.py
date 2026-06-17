content = open(r'.\src\SionyxKiosk\Services\AuthService.cs', encoding='utf-8').read()
idx = content.find('IsLoggedInAsync')
print(content[idx:idx+600])
