path = r'.\src\SionyxKiosk\ViewModels\ProfileViewModel.cs'
content = open(path, encoding='utf-8').read()
print(repr(content[content.find('result.IsSuccess'):content.find('result.IsSuccess')+200]))
