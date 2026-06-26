content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\PaymentDialog.xaml.cs', encoding='utf-8').read()

# Normalize to \n
content_n = content.replace('\r\n', '\n')

old = '            Logger.Information("Crediting user {UserId}: +{Min}min +{Prints} prints", userId, addMinutes, addPrints);\n            // Update purchase status\n            await _firebase.DbUpdateAsync($"purchases/{_purchaseId}", new Dictionary<string, object>\n            {\n                ["status"] = "completed",\n                ["creditedAt"] = DateTime.UtcNow.ToString("o"),\n                ["creditedBy"] = "kiosk-direct"\n            });\n            // Credit user\n            await _firebase.DbUpdateAsync($"users/{userId}", new Dictionary<string, object>\n            {\n                ["remainingTime"] = newTime,\n                ["printBalance"] = newPrints,\n                ["lastCreditedAt"] = DateTime.UtcNow.ToString("o"),\n                ["lastCreditedBy"] = "kiosk-direct"\n            });\n            Logger.Information("User {UserId} credited successfully. newTime={T} newPrints={P}", userId, newTime, newPrints);'

new = '            // Extract KevaId from JS response (saved card token from Nedarim)\n            var kevaId = "";\n            if (root.TryGetProperty("response", out var resp) && resp.ValueKind == System.Text.Json.JsonValueKind.Object)\n            {\n                kevaId = resp.TryGetProperty("KevaId", out var keva) ? keva.GetString() ?? "" : "";\n                if (!string.IsNullOrEmpty(kevaId))\n                    Logger.Information("KevaId received: {KevaId}", kevaId);\n            }\n            Logger.Information("Crediting user {UserId}: +{Min}min +{Prints} prints", userId, addMinutes, addPrints);\n            // Update purchase status\n            await _firebase.DbUpdateAsync($"purchases/{_purchaseId}", new Dictionary<string, object>\n            {\n                ["status"] = "completed",\n                ["creditedAt"] = DateTime.UtcNow.ToString("o"),\n                ["creditedBy"] = "kiosk-direct"\n            });\n            // Credit user\n            var userUpdate = new Dictionary<string, object>\n            {\n                ["remainingTime"] = newTime,\n                ["printBalance"] = newPrints,\n                ["lastCreditedAt"] = DateTime.UtcNow.ToString("o"),\n                ["lastCreditedBy"] = "kiosk-direct"\n            };\n            if (!string.IsNullOrEmpty(kevaId))\n            {\n                userUpdate["savedCard"] = new Dictionary<string, object> { ["kevaId"] = kevaId, ["savedAt"] = DateTime.UtcNow.ToString("o") };\n                Logger.Information("Saving KevaId for user {UserId}", userId);\n            }\n            await _firebase.DbUpdateAsync($"users/{userId}", userUpdate);\n            Logger.Information("User {UserId} credited successfully. newTime={T} newPrints={P}", userId, newTime, newPrints);'

count = content_n.count(old)
print(f"Found {count} matches")
if count == 1:
    result = content_n.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\PaymentDialog.xaml.cs', 'w', encoding='utf-8', newline='\r\n').write(result)
    print('OK')
else:
    print('NOT FOUND')
