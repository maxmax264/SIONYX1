content = open(r'.\src\SionyxKiosk\App.xaml.cs', encoding='utf-8').read()
idx = content.find('_trayIcon.ExitRequested')
print(content[idx:idx+200])
