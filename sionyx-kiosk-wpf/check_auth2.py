content = open(r'.\src\SionyxKiosk\Services\AuthService.cs', encoding='utf-8').read()
idx = content.find('currentComputerId')
print(content[idx-300:idx+400])
