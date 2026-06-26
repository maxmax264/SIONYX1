path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\PaymentDialog.xaml.cs'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

old = '''                case "chargeWithSavedCard":
                    await HandleChargeWithSavedCardAsync(root);
                    break;'''

new = '''                case "chargeWithSavedCard":
                    await HandleChargeWithSavedCardAsync();
                    break;'''

count = content_n.count(old)
print(f"Step A - Found {count} matches")
if count == 1:
    content_n = content_n.replace(old, new, 1)
    print("Step A OK")
else:
    print("Step A NOT FOUND - aborting")
    exit()

old2 = '    private async Task HandleChargeWithSavedCardAsync(JsonElement root)\n    {'
new2 = '''    // Note: Nedarim's TashlumBodedNew API (charging an existing saved card/Keva) does not accept
    // a CVV parameter at all - per their docs, CVV is never stored and cannot be verified for
    // an existing token charge. The CVV field in the UI is a client-side UX prompt only.
    private async Task HandleChargeWithSavedCardAsync()
    {'''

count2 = content_n.count(old2)
print(f"Step B - Found {count2} matches")
if count2 == 1:
    content_n = content_n.replace(old2, new2, 1)
    open(path, 'w', encoding='utf-8', newline='\r\n').write(content_n)
    print("Step B OK - file saved")
else:
    print("Step B NOT FOUND - aborting, file NOT saved")
