path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\PaymentDialog.xaml.cs'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

# Step 1: Replace the broken "wait for listener that never fires" code in HandleChargeWithSavedCardAsync
old1 = '''            if (status == "OK")
            {
                // Trigger success flow via Firebase callback listener
                StartPurchaseStatusListener(_purchaseId);
                var msg = JsonSerializer.Serialize(new { action = "savedCardCharging" });
                _ = Dispatcher.InvokeAsync(() => PaymentWebView.CoreWebView2.PostWebMessageAsJson(msg));
            }'''

new1 = '''            if (status == "OK")
            {
                // Charge succeeded immediately - credit the user directly (no callback exists for this flow)
                await CreditUserForPurchaseAsync(_purchaseId, savedKevaId);
            }'''

count1 = content_n.count(old1)
print(f"Step 1 - Found {count1} matches")
if count1 == 1:
    content_n = content_n.replace(old1, new1, 1)
    print("Step 1 OK")
else:
    print("Step 1 NOT FOUND - aborting")
    exit()

# Step 2: Extract shared crediting logic into a new method, refactor HandlePaymentSuccessAsync to use it
old2 = '''    private async Task HandlePaymentSuccessAsync(JsonElement root)
    {
        Logger.Information("Payment success received from JS - raw: {Raw}", root.ToString());

        if (string.IsNullOrEmpty(_purchaseId)) return;

        try
        {
            // Read purchase data to get package details
            var purchaseResult = await _firebase.DbGetAsync($"purchases/{_purchaseId}");
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
            var userResult = await _firebase.DbGetAsync($"users/{userId}");
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

            // Extract KevaId from JS response
            var kevaId = "";
            if (root.TryGetProperty("response", out var resp) && resp.ValueKind == System.Text.Json.JsonValueKind.Object)
            {
                kevaId = resp.TryGetProperty("KevaId", out var keva) ? keva.GetString() ?? "" : "";
                if (!string.IsNullOrEmpty(kevaId))
                    Logger.Information("KevaId received: {KevaId}", kevaId);
            }
            Logger.Information("Crediting user {UserId}: +{Min}min +{Prints} prints", userId, addMinutes, addPrints);

            // Update purchase status
            await _firebase.DbUpdateAsync($"purchases/{_purchaseId}", new Dictionary<string, object>
            {
                ["status"] = "completed",
                ["creditedAt"] = DateTime.UtcNow.ToString("o"),
                ["creditedBy"] = "kiosk-direct"
            });

            // Credit user
            var userUpdate = new Dictionary<string, object>
            {
                ["remainingTime"] = newTime,
                ["printBalance"] = newPrints,
                ["lastCreditedAt"] = DateTime.UtcNow.ToString("o"),
                ["lastCreditedBy"] = "kiosk-direct"
            };
            if (!string.IsNullOrEmpty(kevaId))
            {
                userUpdate["savedCard"] = new Dictionary<string, object> { ["kevaId"] = kevaId, ["savedAt"] = DateTime.UtcNow.ToString("o") };
                Logger.Information("Saving KevaId for user {UserId}", userId);
            }
            await _firebase.DbUpdateAsync($"users/{userId}", userUpdate);

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
    }'''

new2 = '''    private async Task HandlePaymentSuccessAsync(JsonElement root)
    {
        Logger.Information("Payment success received from JS - raw: {Raw}", root.ToString());

        if (string.IsNullOrEmpty(_purchaseId)) return;

        // Extract KevaId from JS response (present only when a token/Keva was created via the iframe)
        var kevaId = "";
        if (root.TryGetProperty("response", out var resp) && resp.ValueKind == System.Text.Json.JsonValueKind.Object)
        {
            kevaId = resp.TryGetProperty("KevaId", out var keva) ? keva.GetString() ?? "" : "";
        }

        await CreditUserForPurchaseAsync(_purchaseId, kevaId);
    }

    /// <summary>
    /// Credits a user for a completed purchase: reads purchase + user data, updates remainingTime/printBalance,
    /// marks the purchase as completed, optionally saves a KevaId for future saved-card charges, and notifies JS.
    /// Used both for the iframe payment flow and the saved-card (TashlumBodedNew) flow, since the latter has
    /// no callback mechanism and must credit synchronously right after a successful charge.
    /// </summary>
    private async Task CreditUserForPurchaseAsync(string purchaseId, string kevaId)
    {
        try
        {
            // Read purchase data to get package details
            var purchaseResult = await _firebase.DbGetAsync($"purchases/{purchaseId}");
            if (!purchaseResult.Success || purchaseResult.Data is not JsonElement purchaseData)
            {
                Logger.Error("Failed to read purchase data for {Id}", purchaseId);
                await ShowTimeoutAsync();
                return;
            }

            var userId = purchaseData.TryGetProperty("userId", out var u) ? u.GetString() : null;
            if (string.IsNullOrEmpty(userId))
            {
                Logger.Error("Purchase {Id} missing userId", purchaseId);
                await ShowTimeoutAsync();
                return;
            }

            // Read current user data
            var userResult = await _firebase.DbGetAsync($"users/{userId}");
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

            if (!string.IsNullOrEmpty(kevaId))
                Logger.Information("KevaId received: {KevaId}", kevaId);
            Logger.Information("Crediting user {UserId}: +{Min}min +{Prints} prints", userId, addMinutes, addPrints);

            // Update purchase status
            await _firebase.DbUpdateAsync($"purchases/{purchaseId}", new Dictionary<string, object>
            {
                ["status"] = "completed",
                ["creditedAt"] = DateTime.UtcNow.ToString("o"),
                ["creditedBy"] = "kiosk-direct"
            });

            // Credit user
            var userUpdate = new Dictionary<string, object>
            {
                ["remainingTime"] = newTime,
                ["printBalance"] = newPrints,
                ["lastCreditedAt"] = DateTime.UtcNow.ToString("o"),
                ["lastCreditedBy"] = "kiosk-direct"
            };
            if (!string.IsNullOrEmpty(kevaId))
            {
                userUpdate["savedCard"] = new Dictionary<string, object> { ["kevaId"] = kevaId, ["savedAt"] = DateTime.UtcNow.ToString("o") };
                Logger.Information("Saving KevaId for user {UserId}", userId);
            }
            await _firebase.DbUpdateAsync($"users/{userId}", userUpdate);

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
    }'''

count2 = content_n.count(old2)
print(f"Step 2 - Found {count2} matches")
if count2 == 1:
    content_n = content_n.replace(old2, new2, 1)
    open(path, 'w', encoding='utf-8', newline='\r\n').write(content_n)
    print("Step 2 OK - file saved")
else:
    print("Step 2 NOT FOUND - aborting, file NOT saved")
