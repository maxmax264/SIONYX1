content = open(r'.\src\SionyxKiosk\ViewModels\ProfileViewModel.cs', encoding='utf-8').read()
old = 'using SionyxKiosk.Services;'
new = 'using SionyxKiosk.Services;'
# just check what's there
idx = content.find('using')
print(repr(content[:200]))
