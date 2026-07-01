path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\PaymentDialog.xaml.cs'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

old = '''            var callbackUrl = $"https://us-central1-{_firebase.ProjectId}.cloudfunctions.net/nedarimCallback";
            // Check if user has a saved card
            var savedKevaId = "";
            var userResult = await _firebase.DbGetAsync($"users/{_userId}");
            if (userResult.Success && userResult.Data is JsonElement userData)
            {
                if (userData.TryGetProperty("savedCard", out var sc) &&
                    sc.TryGetProperty("kevaId", out var keva))
                    savedKevaId = keva.GetString() ?? "";
            }

            var config = new
            {
                mosadId,
                apiValid,
                amount = _package.DisplayPrice.ToString("F0"),
                packageName = _package.Name ?? "",
                packageMinutes = _package.Minutes.ToString(),
                packagePrints = _package.Prints.ToString(),
                userName = "",
                orgId = _firebase.OrgId,
                callbackUrl,
                saveCardEnabled,
                saveCardApiValid,
                savedKevaId
            };'''

new = '''            var callbackUrl = $"https://us-central1-{_firebase.ProjectId}.cloudfunctions.net/nedarimCallback";
            // Check if user has a saved card, and read their name for the payment form
            var savedKevaId = "";
            var userName = "";
            var userResult = await _firebase.DbGetAsync($"users/{_userId}");
            if (userResult.Success && userResult.Data is JsonElement userData)
            {
                if (userData.TryGetProperty("savedCard", out var sc) &&
                    sc.TryGetProperty("kevaId", out var keva))
                    savedKevaId = keva.GetString() ?? "";

                var firstName = userData.TryGetProperty("firstName", out var fn) ? fn.GetString() ?? "" : "";
                var lastName = userData.TryGetProperty("lastName", out var ln) ? ln.GetString() ?? "" : "";
                userName = $"{firstName} {lastName}".Trim();
            }

            var config = new
            {
                mosadId,
                apiValid,
                amount = _package.DisplayPrice.ToString("F0"),
                packageName = _package.Name ?? "",
                packageMinutes = _package.Minutes.ToString(),
                packagePrints = _package.Prints.ToString(),
                userName,
                orgId = _firebase.OrgId,
                callbackUrl,
                saveCardEnabled,
                saveCardApiValid,
                savedKevaId
            };'''

count = content_n.count(old)
print(f"Found {count} matches")
if count == 1:
    content_n = content_n.replace(old, new, 1)
    open(path, 'w', encoding='utf-8', newline='\r\n').write(content_n)
    print("OK - file saved")
else:
    print("NOT FOUND - file NOT saved")
