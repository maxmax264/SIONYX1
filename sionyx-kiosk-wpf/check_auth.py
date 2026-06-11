content = open(r'.\src\SionyxKiosk\Services\AuthService.cs', encoding='utf-8').read()
idx = content.find('isLoggedIn')
print(content[idx-200:idx+400])
