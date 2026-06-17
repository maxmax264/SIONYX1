content = open(r'.\src\SionyxKiosk\App.xaml.cs', encoding='utf-8').read()
idx = content.find('ShowAuthWindow();')
print(repr(content[idx-200:idx+50]))
