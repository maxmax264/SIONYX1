content = open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', encoding='utf-8').read()

idx = content.find('public void StopMonitoring()')
print(repr(content[idx:idx+400]))
