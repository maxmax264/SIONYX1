path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\PaymentDialog.xaml.cs'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

old = '''        // Extract KevaId/LastNum/Tokef from JS response (present only when a token/Keva was
        // created via the iframe). Nedarim does not store the expiry date for tokens - we keep
        // it ourselves so it can be displayed to the user next time without re-asking for it.
        var kevaId = "";
        var lastNum = "";
        var expiry = "";
        if (root.TryGetProperty("response", out var resp) && resp.ValueKind == System.Text.Json.JsonValueKind.Object)
        {
            kevaId = resp.TryGetProperty("KevaId", out var keva) ? keva.GetString() ?? "" : "";
            lastNum = resp.TryGetProperty("LastNum", out var ln) ? ln.GetString() ?? "" : "";
            expiry = resp.TryGetProperty("Tokef", out var tk) ? tk.GetString() ?? "" : "";
        }

        await CreditUserForPurchaseAsync(_purchaseId, kevaId, lastNum, expiry);'''

new = '''        // Extract KevaId/LastNum from JS response (present only when a token/Keva was created
        // via the iframe). Nedarim hides the expiry field when creating a token (Tokef=Hide is
        // required for CreateToken to actually work), so it never comes back in the response -
        // we read what the user typed into our own expiry field instead, and keep it ourselves.
        var kevaId = "";
        var lastNum = "";
        if (root.TryGetProperty("response", out var resp) && resp.ValueKind == System.Text.Json.JsonValueKind.Object)
        {
            kevaId = resp.TryGetProperty("KevaId", out var keva) ? keva.GetString() ?? "" : "";
            lastNum = resp.TryGetProperty("LastNum", out var ln) ? ln.GetString() ?? "" : "";
        }
        var expiry = root.TryGetProperty("enteredExpiry", out var ee) ? ee.GetString() ?? "" : "";

        await CreditUserForPurchaseAsync(_purchaseId, kevaId, lastNum, expiry);'''

count = content_n.count(old)
print(f"Found {count} matches")
if count == 1:
    content_n = content_n.replace(old, new, 1)
    open(path, 'w', encoding='utf-8', newline='\r\n').write(content_n)
    print("OK - file saved")
else:
    print("NOT FOUND - file NOT saved")
