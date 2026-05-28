content = open(r'.\src\SionyxKiosk\Services\SessionService.cs', encoding='utf-8').read()
idx = content.find('OperatingHours.StartMonitoring')
print(repr(content[idx-4:idx+120]))
