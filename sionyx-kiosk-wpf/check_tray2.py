content = open(r'.\src\SionyxKiosk\Services\TrayIconService.cs', encoding='utf-8').read()
idx = content.find('var menu = new ContextMenu()')
print(repr(content[idx:idx+200]))
