lines = open(r'.\src\SionyxKiosk\Services\SessionService.cs', encoding='utf-8').readlines()

# מצא את FetchFreshRemainingTimeAsync ותחליף את שתי הפונקציות הישנות בפונקציה אחת חדשה
start = next(i for i,l in enumerate(lines) if 'private async Task<int?> FetchFreshRemainingTimeAsync' in l)
end = next(i for i,l in enumerate(lines) if 'Error checking time expiration' in l)
end = next(i for i,l in enumerate(lines) if '    }' in l and i > end)

new_func = [
'    private record UserValidationResult(bool Valid, int RemainingTime, string? ErrorMessage);\n',
'    private async Task<UserValidationResult> FetchAndValidateUserAsync(int fallbackTime)\n',
'    {\n',
'        try\n',
'        {\n',
'            var result = await Firebase.DbGetAsync($"users/{_userId}");\n',
'            if (!result.Success || result.Data is not System.Text.Json.JsonElement data || data.ValueKind == System.Text.Json.JsonValueKind.Null)\n',
'                return new(fallbackTime > 0, fallbackTime, fallbackTime <= 0 ? "No time remaining" : null);\n',
'            var remainingTime = fallbackTime;\n',
'            if (data.TryGetProperty("remainingTime", out var rt) && rt.TryGetInt32(out var seconds))\n',
'            {\n',
'                Logger.Information("Fresh remainingTime from Firebase: {Seconds}s", seconds);\n',
'                remainingTime = seconds;\n',
'            }\n',
'            var expiresAtStr = data.TryGetProperty("timeExpiresAt", out var te) ? te.GetString() : null;\n',
'            if (!string.IsNullOrEmpty(expiresAtStr) &&\n',
'                DateTime.TryParse(expiresAtStr, out var expiresAt) &&\n',
'                DateTime.Now > expiresAt)\n',
'            {\n',
'                _ = Firebase.DbUpdateAsync($"users/{_userId}", new Dictionary<string, object?>\n',
'                {\n',
'                    ["remainingTime"] = 0,\n',
'                    ["timeExpiresAt"] = null,\n',
'                    ["updatedAt"] = DateTime.Now.ToString("o"),\n',
'                });\n',
'                return new(false, 0, "הזמן שלך פג תוקף. אנא רכוש חבילה חדשה.");\n',
'            }\n',
'            if (remainingTime <= 0)\n',
'                return new(false, 0, "No time remaining");\n',
'            return new(true, remainingTime, null);\n',
'        }\n',
'        catch (Exception ex)\n',
'        {\n',
'            Logger.Warning(ex, "Failed to fetch user data, using local value");\n',
'            return new(fallbackTime > 0, fallbackTime, fallbackTime <= 0 ? "No time remaining" : null);\n',
'        }\n',
'    }\n',
]

lines[start:end+1] = new_func
open(r'.\src\SionyxKiosk\Services\SessionService.cs', 'w', encoding='utf-8').writelines(lines)
print(f'OK - replaced lines {start+1} to {end+1}')
