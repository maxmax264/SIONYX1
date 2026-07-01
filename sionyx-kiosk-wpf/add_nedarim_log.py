path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\PaymentDialog.xaml.cs'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

old = '''            var formData = new FormUrlEncodedContent(formFields);
            var response = await http.PostAsync("https://matara.pro/nedarimplus/Reports/Manage3.aspx", formData);'''

new = '''            Logger.Information("Nedarim TashlumBodedNew request: MosadNumber={MosadId} ApiPassword={ApiPassword} KevaId={KevaId} Amount={Amount} Tokef={Tokef}",
                mosadId, apiPassword, savedKevaId, _package.DisplayPrice.ToString("F0"), savedExpiry);
            var formData = new FormUrlEncodedContent(formFields);
            var response = await http.PostAsync("https://matara.pro/nedarimplus/Reports/Manage3.aspx", formData);'''

count = content_n.count(old)
print(f"Found {count} matches")
if count == 1:
    content_n = content_n.replace(old, new, 1)
    open(path, 'w', encoding='utf-8', newline='\r\n').write(content_n)
    print("OK - file saved")
else:
    print("NOT FOUND - file NOT saved")
