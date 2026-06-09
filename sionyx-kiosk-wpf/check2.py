content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs', encoding='utf-8').read()
idx = content.find('CleanupWithBrowserClose')
print(repr(content[idx-200:idx+100]))
