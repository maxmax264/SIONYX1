content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\PaymentDialog.xaml.cs', encoding='utf-8').read()

old = '''            var purchaseResult = await _firebase.DbGetAsync($"organizations/{_firebase.OrgId}/purchases/{_purchaseId}");'''
new = '''            var purchaseResult = await _firebase.DbGetAsync($"purchases/{_purchaseId}");'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\PaymentDialog.xaml.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
