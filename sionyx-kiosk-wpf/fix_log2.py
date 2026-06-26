content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\PaymentDialog.xaml.cs', encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

old = '        Logger.Information("Payment success received from JS");\n\n        if (string.IsNullOrEmpty(_purchaseId)) return;'
new = '        Logger.Information("Payment success received from JS - raw: {Raw}", root.ToString());\n\n        if (string.IsNullOrEmpty(_purchaseId)) return;'

count = content_n.count(old)
print(f"Found {count} matches")
if count == 1:
    result = content_n.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\PaymentDialog.xaml.cs', 'w', encoding='utf-8', newline='\r\n').write(result)
    print('OK')
else:
    print('NOT FOUND')
