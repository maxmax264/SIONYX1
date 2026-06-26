content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs', encoding='utf-8-sig', errors='replace').read()

old = '_trayIcon.OpenControlPanelRequested += () =>'
idx = content.find(old)
print(repr(content[idx:idx+300]))
