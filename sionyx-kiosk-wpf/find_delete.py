content = open(r'.\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8').read()

idx = content.find('Directory.Delete(profilePath, true);')
print(repr(content[idx-200:idx+200]))
