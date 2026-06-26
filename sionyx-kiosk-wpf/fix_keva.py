content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\PaymentDialog.xaml.cs', encoding='utf-8').read()

old = '''            Logger.Information("Crediting user {UserId}: +{Min}min +{Prints} prints", userId, addMinutes, addPrints);
            // Update purchase status
            await _firebase.DbUpdateAsync($"purchases/{_purchaseId}", new Dictionary<string, object>
            {
                ["status"] = "completed",
                ["creditedAt"] = DateTime.UtcNow.ToString("o"),
                ["creditedBy"] = "kiosk-direct"
            });
            // Credit user
            await _firebase.DbUpdateAsync($"users/{userId}", new Dictionary<string, object>
            {
                ["remainingTime"] = newTime,
                ["printBalance"] = newPrints,
                ["lastCreditedAt"] = DateTime.UtcNow.ToString("o"),
                ["lastCreditedBy"] = "kiosk-direct"
            });'''

new = '''            // Extract KevaId from JS response (saved card token from Nedarim)
            var kevaId = "";
            if (root.TryGetProperty("response", out var resp) && resp.ValueKind == JsonValueKind.Object)
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
            // Save KevaId if returned (saved card token)
            if (!string.IsNullOrEmpty(kevaId))
            {
                userUpdate["savedCard"] = new Dictionary<string, object>
                {
                    ["kevaId"] = kevaId,
                    ["savedAt"] = DateTime.UtcNow.ToString("o")
                };
                Logger.Information("Saving KevaId for user {UserId}", userId);
            }
            await _firebase.DbUpdateAsync($"users/{userId}", userUpdate);'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\PaymentDialog.xaml.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
