path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\PaymentDialog.xaml.cs'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

old = "                case \"close\":\n                    var success = root.TryGetProperty(\"success\", out var s) && s.GetBoolean();\n                    PaymentSucceeded = success;\n                    _ = Dispatcher.InvokeAsync(Close);\n                    break;"

new = "                case \"chargeWithSavedCard\":\n                    await HandleChargeWithSavedCardAsync(root);\n                    break;\n                case \"deleteCard\":\n                    await HandleDeleteCardAsync();\n                    break;\n                case \"close\":\n                    var success = root.TryGetProperty(\"success\", out var s) && s.GetBoolean();\n                    PaymentSucceeded = success;\n                    _ = Dispatcher.InvokeAsync(Close);\n                    break;"

count = content_n.count(old)
print(f"Found {count} matches")
if count == 1:
    result = content_n.replace(old, new, 1)
    open(path, 'w', encoding='utf-8', newline='\r\n').write(result)
    print('OK')
else:
    print('NOT FOUND')
