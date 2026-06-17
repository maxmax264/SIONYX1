content = open(r'.\src\SionyxKiosk\App.xaml.cs', encoding='utf-8').read()
idx = content.find('RestoreRequested += () =>')
print(content[idx:idx+600])
