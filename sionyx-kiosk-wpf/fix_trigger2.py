content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8').read()
idx = content.find('<Triggers/>')
print(repr(content[idx:idx+200]))
