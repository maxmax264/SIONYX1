content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\PaymentDialog.xaml.cs', encoding='utf-8').read()

old = '''    private async Task HandlePaymentSuccessAsync(JsonElement root)
    {
        Logger.Information("Payment success received from JS");

        // Give the Cloud Function callback a head start before polling.
        await Task.Delay(TimeSpan.FromSeconds(2));

        if (!PaymentSucceeded)
            await PollPurchaseStatusAsync();
    }'''

new = '''    private async Task HandlePaymentSuccessAsync(JsonElement root)
    {
        Logger.Information("Payment success received from JS");

        if (string.IsNullOrEmpty(_purchaseId)) return;

        try
        {
            // Read purchase data to get package details
            var purchaseResult = await _firebase.DbGetAsync($"organizations/{_firebase.OrgId}/purchases/{_purchaseId}");
            if (!purchaseResult.Success || purchaseResult.Data is not JsonElement purchaseData)
            {
                Logger.Error("Failed to read purchase data for {Id}", _purchaseId);
                await ShowTimeoutAsync();
                return;
            }

            var userId = purchaseData.TryGetProperty("userId", out var u) ? u.GetString() : null;
            if (string.IsNullOrEmpty(userId))
            {
                Logger.Error("Purchase {Id} missing userId", _purchaseId);
                await ShowTimeoutAsync();
                return;
            }

            // Read current user data
            var userResult = await _firebase.DbGetAsync($"organizations/{_firebase.OrgId}/users/{userId}");
            if (!userResult.Success || userResult.Data is not JsonElement userData)
            {
                Logger.Error("Failed to read user data for {UserId}", userId);
                await ShowTimeoutAsync();
                return;
            }

            var currentTime = userData.TryGetProperty("remainingTime", out var rt) ? rt.GetInt32() : 0;
            var currentPrints = userData.TryGetProperty("printBalance", out var pb) ? pb.GetDouble() : 0.0;
            var addMinutes = purchaseData.TryGetProperty("minutes", out var m) ? m.GetInt32() : 0;
            var addPrints = purchaseData.TryGetProperty("printBudget", out var pp) ? pp.GetDouble() : 0.0;

            var newTime = currentTime + (addMinutes * 60);
            var newPrints = currentPrints + addPrints;

            Logger.Information("Crediting user {UserId}: +{Min}min +{Prints} prints", userId, addMinutes, addPrints);

            // Update purchase status
            await _firebase.DbUpdateAsync($"organizations/{_firebase.OrgId}/purchases/{_purchaseId}", new Dictionary<string, object>
            {
                ["status"] = "completed",
                ["creditedAt"] = DateTime.UtcNow.ToString("o"),
                ["creditedBy"] = "kiosk-direct"
            });

            // Credit user
            await _firebase.DbUpdateAsync($"organizations/{_firebase.OrgId}/users/{userId}", new Dictionary<string, object>
            {
                ["remainingTime"] = newTime,
                ["printBalance"] = newPrints,
                ["lastCreditedAt"] = DateTime.UtcNow.ToString("o"),
                ["lastCreditedBy"] = "kiosk-direct"
            });

            Logger.Information("User {UserId} credited successfully. newTime={T} newPrints={P}", userId, newTime, newPrints);

            _ = Dispatcher.InvokeAsync(() =>
            {
                PaymentSucceeded = true;
                var msg = System.Text.Json.JsonSerializer.Serialize(new { action = "showSuccess" });
                PaymentWebView.CoreWebView2.PostWebMessageAsJson(msg);
            });
        }
        catch (Exception ex)
        {
            Logger.Error(ex, "Failed to credit user after payment");
            await ShowTimeoutAsync();
        }
    }

    private Task ShowTimeoutAsync()
    {
        _ = Dispatcher.InvokeAsync(() =>
        {
            var msg = System.Text.Json.JsonSerializer.Serialize(new { action = "showTimeout" });
            PaymentWebView.CoreWebView2.PostWebMessageAsJson(msg);
        });
        return Task.CompletedTask;
    }'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\PaymentDialog.xaml.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
