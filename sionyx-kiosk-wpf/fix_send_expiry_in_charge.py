path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\PaymentDialog.xaml.cs'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

old = '''            // Read savedKevaId from Firebase
            var savedKevaId = "";
            var userResult = await _firebase.DbGetAsync($"users/{_userId}");
            if (userResult.Success && userResult.Data is JsonElement userData)
            {
                if (userData.TryGetProperty("savedCard", out var sc) &&
                    sc.TryGetProperty("kevaId", out var keva))
                    savedKevaId = keva.GetString() ?? "";
            }
            if (string.IsNullOrEmpty(savedKevaId))
            {
                var errMsg = JsonSerializer.Serialize(new { action = "purchaseError", error = "לא נמצא כרטיס שמור" });
                _ = Dispatcher.InvokeAsync(() => PaymentWebView.CoreWebView2.PostWebMessageAsJson(errMsg));
                return;
            }

            // Call Nedarim TashlumBodedNew
            Logger.Information("Charging with saved card KevaId={KevaId} PurchaseId={PurchaseId}", savedKevaId, _purchaseId);
            using var http = new HttpClient();
            http.Timeout = TimeSpan.FromSeconds(30);
            var formData = new FormUrlEncodedContent(new Dictionary<string, string>
            {
                ["Action"] = "TashlumBodedNew",
                ["MosadNumber"] = mosadId,
                ["ApiPassword"] = apiPassword,
                ["Currency"] = "1",
                ["KevaId"] = savedKevaId,
                ["Amount"] = _package.DisplayPrice.ToString("F0"),
                ["Tashloumim"] = "1",
                ["JoinToKevaId"] = "NoJoin",
                ["Comments"] = $"Purchase:{_purchaseId}"
            });'''

new = '''            // Read savedKevaId (+ stored expiry, for an experiment - see comment below) from Firebase
            var savedKevaId = "";
            var savedExpiry = "";
            var userResult = await _firebase.DbGetAsync($"users/{_userId}");
            if (userResult.Success && userResult.Data is JsonElement userData)
            {
                if (userData.TryGetProperty("savedCard", out var sc))
                {
                    savedKevaId = sc.TryGetProperty("kevaId", out var keva) ? keva.GetString() ?? "" : "";
                    savedExpiry = sc.TryGetProperty("expiry", out var exp) ? exp.GetString() ?? "" : "";
                }
            }
            if (string.IsNullOrEmpty(savedKevaId))
            {
                var errMsg = JsonSerializer.Serialize(new { action = "purchaseError", error = "לא נמצא כרטיס שמור" });
                _ = Dispatcher.InvokeAsync(() => PaymentWebView.CoreWebView2.PostWebMessageAsJson(errMsg));
                return;
            }

            // Call Nedarim TashlumBodedNew. EXPERIMENT: TashlumBodedNew is not documented to accept
            // an expiry/Tokef parameter, but we are testing whether sending the expiry the user
            // entered when the token was created changes anything about whether the charge succeeds.
            // If Nedarim ignores unknown form fields (as most APIs do), this is harmless either way.
            Logger.Information("Charging with saved card KevaId={KevaId} PurchaseId={PurchaseId} (testing with Tokef={Tokef})", savedKevaId, _purchaseId, savedExpiry);
            using var http = new HttpClient();
            http.Timeout = TimeSpan.FromSeconds(30);
            var formFields = new Dictionary<string, string>
            {
                ["Action"] = "TashlumBodedNew",
                ["MosadNumber"] = mosadId,
                ["ApiPassword"] = apiPassword,
                ["Currency"] = "1",
                ["KevaId"] = savedKevaId,
                ["Amount"] = _package.DisplayPrice.ToString("F0"),
                ["Tashloumim"] = "1",
                ["JoinToKevaId"] = "NoJoin",
                ["Comments"] = $"Purchase:{_purchaseId}"
            };
            if (!string.IsNullOrEmpty(savedExpiry))
                formFields["Tokef"] = savedExpiry;
            var formData = new FormUrlEncodedContent(formFields);'''

count = content_n.count(old)
print(f"Found {count} matches")
if count == 1:
    content_n = content_n.replace(old, new, 1)
    open(path, 'w', encoding='utf-8', newline='\r\n').write(content_n)
    print("OK - file saved")
else:
    print("NOT FOUND - file NOT saved")
