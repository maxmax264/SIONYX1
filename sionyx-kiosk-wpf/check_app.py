content = open(r'.\src\SionyxKiosk\App.xaml.cs', encoding='utf-8').read()
# Find ShowMainWindow
idx = content.find('private void ShowMainWindow()')
print(content[idx:idx+500])
print("---")
# Find OnStartup
idx2 = content.find('ShowAuthWindow();')
print(content[idx2-100:idx2+50])
