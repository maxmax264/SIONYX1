path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\PaymentDialog.xaml.cs'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

old = '            var callbackUrl = $"https://us-central1-{_firebase.ProjectId}.cloudfunctions.net/nedarimCallback";\n\n            var config = new\n            {\n                mosadId,\n                apiValid,\n                amount = _package.DisplayPrice.ToString("F0"),\n                packageName = _package.Name ?? "",\n                packageMinutes = _package.Minutes.ToString(),\n                packagePrints = _package.Prints.ToString(),\n                userName = "",\n                orgId = _firebase.OrgId,\n                callbackUrl,\n                saveCardEnabled,\n                saveCardApiValid\n            };'

new = '            var callbackUrl = $"https://us-central1-{_firebase.ProjectId}.cloudfunctions.net/nedarimCallback";\n            // Check if user has a saved card\n            var savedKevaId = "";\n            var userResult = await _firebase.DbGetAsync($"users/{_userId}");\n            if (userResult.Success && userResult.Data is JsonElement userData)\n            {\n                if (userData.TryGetProperty("savedCard", out var sc) &&\n                    sc.TryGetProperty("kevaId", out var keva))\n                    savedKevaId = keva.GetString() ?? "";\n            }\n\n            var config = new\n            {\n                mosadId,\n                apiValid,\n                amount = _package.DisplayPrice.ToString("F0"),\n                packageName = _package.Name ?? "",\n                packageMinutes = _package.Minutes.ToString(),\n                packagePrints = _package.Prints.ToString(),\n                userName = "",\n                orgId = _firebase.OrgId,\n                callbackUrl,\n                saveCardEnabled,\n                saveCardApiValid,\n                savedKevaId\n            };'

count = content_n.count(old)
print(f"Found {count} matches")
if count == 1:
    result = content_n.replace(old, new, 1)
    open(path, 'w', encoding='utf-8', newline='\r\n').write(result)
    print('OK')
else:
    print('NOT FOUND')
