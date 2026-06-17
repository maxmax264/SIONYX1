content = open(r'.\src\SionyxKiosk\Services\SessionService.cs', encoding='utf-8').read()
idx = content.find('StartSessionAsync')
print(content[idx:idx+800])
