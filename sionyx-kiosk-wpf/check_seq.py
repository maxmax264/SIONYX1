content = open(r'.\installer\Package.wxs', encoding='utf-8').read()
idx = content.find('InstallExecuteSequence')
print(content[idx:idx+800])
