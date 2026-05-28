content = open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', encoding='utf-8').read()
idx = content.find('private async Task HandlePausedJobAsync')
print(repr(content[idx:idx+250]))
