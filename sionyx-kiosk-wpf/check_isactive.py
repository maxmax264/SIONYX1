content = open(r'.\src\SionyxKiosk\Services\SessionService.cs', encoding='utf-8').read()
idx = content.find('IsActive = true')
print(repr(content[idx:idx+200]))
