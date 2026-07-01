path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\PaymentDialog.xaml.cs'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

old1 = '''            var callbackUrl = $"https://us-central1-{_firebase.ProjectId}.cloudfunctions.net/nedarimCallback";
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

new1 = '''            var callbackUrl = $"https://us-central1-{_firebase.ProjectId}.cloudfunctions.net/nedarimCallback";
            // Check if user has a saved card, and read their name for the payment form
            var savedKevaId = "";
            var savedCardLastNum = "";
            var savedCardExpiry = "";
            var userName = "";
            var userResult = await _firebase.DbGetAsync($"users/{_userId}");
            if (userResult.Success && userResult.Data is JsonElement userData)
            {
                if (userData.TryGetProperty("savedCard", out var sc))
                {
                    savedKevaId = sc.TryGetProperty("kevaId", out var keva) ? keva.GetString() ?? "" : "";
                    savedCardLastNum = sc.TryGetProperty("lastNum", out var ln2) ? ln2.GetString() ?? "" : "";
                    savedCardExpiry = sc.TryGetProperty("expiry", out var exp) ? exp.GetString() ?? "" : "";
                }

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
                savedKevaId,
                savedCardLastNum,
                savedCardExpiry
            };'''

count1 = content_n.count(old1)
print(f"Found {count1} matches")
if count1 == 1:
    content_n = content_n.replace(old1, new1, 1)
    open(path, 'w', encoding='utf-8', newline='\r\n').write(content_n)
    print("OK - file saved")
else:
    print("NOT FOUND - file NOT saved")
