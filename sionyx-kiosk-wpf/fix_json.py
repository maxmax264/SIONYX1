content = open(r'.\src\SionyxKiosk\Services\SessionService.cs', encoding='utf-8').read()
content = content.replace('System.Text.JsonElement?', 'JsonElement?')
open(r'.\src\SionyxKiosk\Services\SessionService.cs', 'w', encoding='utf-8').write(content)
print('OK')
