content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\PaymentDialog.xaml.cs', encoding='utf-8').read()

content = content.replace(
    f'_firebase.DbUpdateAsync($"organizations/{{_firebase.OrgId}}/purchases/{{_purchaseId}}"',
    f'_firebase.DbUpdateAsync($"purchases/{{_purchaseId}}"'
)
content = content.replace(
    f'_firebase.DbUpdateAsync($"organizations/{{_firebase.OrgId}}/users/{{userId}}"',
    f'_firebase.DbUpdateAsync($"users/{{userId}}"'
)

open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\PaymentDialog.xaml.cs', 'w', encoding='utf-8').write(content)
print('OK')
