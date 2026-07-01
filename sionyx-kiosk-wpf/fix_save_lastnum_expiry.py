path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\PaymentDialog.xaml.cs'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

# Step 1: HandlePaymentSuccessAsync extracts LastNum + Tokef too, and passes them along
old1 = '''    private async Task HandlePaymentSuccessAsync(JsonElement root)
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
    }'''

new1 = '''    private async Task HandlePaymentSuccessAsync(JsonElement root)
    {
        Logger.Information("Payment success received from JS - raw: {Raw}", root.ToString());

        if (string.IsNullOrEmpty(_purchaseId)) return;

        // Extract KevaId/LastNum/Tokef from JS response (present only when a token/Keva was
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

        await CreditUserForPurchaseAsync(_purchaseId, kevaId, lastNum, expiry);
    }'''

count1 = content_n.count(old1)
print(f"Step 1 - Found {count1} matches")
if count1 == 1:
    content_n = content_n.replace(old1, new1, 1)
    print("Step 1 OK")
else:
    print("Step 1 NOT FOUND - aborting")
    exit()

# Step 2: HandleChargeWithSavedCardAsync call site - pass empty lastNum/expiry (no new card info here)
old2 = '''            if (status == "OK")
            {
                // Charge succeeded immediately - credit the user directly (no callback exists for this flow)
                await CreditUserForPurchaseAsync(_purchaseId, savedKevaId);
            }'''

new2 = '''            if (status == "OK")
            {
                // Charge succeeded immediately - credit the user directly (no callback exists for this flow).
                // No new card info to save here - lastNum/expiry stay as already stored for this KevaId.
                await CreditUserForPurchaseAsync(_purchaseId, savedKevaId, lastNum: null, expiry: null);
            }'''

count2 = content_n.count(old2)
print(f"Step 2 - Found {count2} matches")
if count2 == 1:
    content_n = content_n.replace(old2, new2, 1)
    print("Step 2 OK")
else:
    print("Step 2 NOT FOUND - aborting")
    exit()

# Step 3: CreditUserForPurchaseAsync signature + body - accept and save lastNum/expiry
old3 = '''    private async Task CreditUserForPurchaseAsync(string purchaseId, string kevaId)
    {'''

new3 = '''    private async Task CreditUserForPurchaseAsync(string purchaseId, string kevaId, string? lastNum = null, string? expiry = null)
    {'''

count3 = content_n.count(old3)
print(f"Step 3 - Found {count3} matches")
if count3 == 1:
    content_n = content_n.replace(old3, new3, 1)
    print("Step 3 OK")
else:
    print("Step 3 NOT FOUND - aborting")
    exit()

old4 = '''            if (!string.IsNullOrEmpty(kevaId))
            {
                userUpdate["savedCard"] = new Dictionary<string, object> { ["kevaId"] = kevaId, ["savedAt"] = DateTime.UtcNow.ToString("o") };
                Logger.Information("Saving KevaId for user {UserId}", userId);
            }'''

new4 = '''            if (!string.IsNullOrEmpty(kevaId))
            {
                var savedCard = new Dictionary<string, object> { ["kevaId"] = kevaId, ["savedAt"] = DateTime.UtcNow.ToString("o") };
                if (!string.IsNullOrEmpty(lastNum)) savedCard["lastNum"] = lastNum;
                if (!string.IsNullOrEmpty(expiry)) savedCard["expiry"] = expiry;
                userUpdate["savedCard"] = savedCard;
                Logger.Information("Saving KevaId for user {UserId} (lastNum={LastNum}, expiry={Expiry})", userId, lastNum, expiry);
            }'''

count4 = content_n.count(old4)
print(f"Step 4 - Found {count4} matches")
if count4 == 1:
    content_n = content_n.replace(old4, new4, 1)
    open(path, 'w', encoding='utf-8', newline='\r\n').write(content_n)
    print("Step 4 OK - file saved")
else:
    print("Step 4 NOT FOUND - file NOT saved")
