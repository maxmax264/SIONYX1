content = open(r'.\src\SionyxKiosk\Services\AuthService.cs', encoding='utf-8').read()
idx = content.find('isLoggedIn", out var loggedIn')
print(content[idx-300:idx+400])
