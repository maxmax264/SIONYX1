content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\PaymentDialog.xaml.cs', encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')
idx = content_n.find('Crediting user')
print(repr(content_n[idx-12:idx+500]))
