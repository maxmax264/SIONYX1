content = open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', encoding='utf-8').read()
idx = content.find('HandlePausedJobAsync')
print(repr(content[idx-4:idx+200]))
