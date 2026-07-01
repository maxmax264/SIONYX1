path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\PaymentDialog.xaml.cs'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

old = '''        var kevaId = "";
        var lastNum = "";
        if (root.TryGetProperty("response", out var resp) && resp.ValueKind == System.Text.Json.JsonValueKind.Object)
        {
            kevaId = resp.TryGetProperty("KevaId", out var keva) ? keva.GetString() ?? "" : "";
            lastNum = resp.TryGetProperty("LastNum", out var ln) ? ln.GetString() ?? "" : "";
        }'''

new = '''        var kevaId = "";
        var lastNum = "";
        if (root.TryGetProperty("response", out var resp) && resp.ValueKind == System.Text.Json.JsonValueKind.Object)
        {
            // Nedarim returns the saved-card identifier under "KevaId" for standing-order (HK)
            // flows, but under "Token" for PaymentType=CreateToken - confirmed empirically from
            // logs (response was {"Status":"OK","Token":"742713","LastNum":"0351"}, no KevaId key
            // at all). We check both so either flow ends up saving the identifier correctly.
            kevaId = resp.TryGetProperty("KevaId", out var keva) ? keva.GetString() ?? "" : "";
            if (string.IsNullOrEmpty(kevaId))
                kevaId = resp.TryGetProperty("Token", out var tok) ? tok.GetString() ?? "" : "";
            lastNum = resp.TryGetProperty("LastNum", out var ln) ? ln.GetString() ?? "" : "";
        }'''

count = content_n.count(old)
print(f"Found {count} matches")
if count == 1:
    content_n = content_n.replace(old, new, 1)
    open(path, 'w', encoding='utf-8', newline='\r\n').write(content_n)
    print("OK - file saved")
else:
    print("NOT FOUND - file NOT saved")
