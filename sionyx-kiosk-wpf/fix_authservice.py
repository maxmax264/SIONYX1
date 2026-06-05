content = open(r'.\src\SionyxKiosk\Services\AuthService.cs', encoding='utf-8').read()
addition = '''
    /// <summary>Check if phone verification is required and if the current user has verified.</summary>
    public async Task<(bool Required, bool Verified)> CheckPhoneVerificationAsync()
    {
        try
        {
            var settingResult = await Firebase.DbGetAsync("metadata/settings/requirePhoneVerification");
            bool required = settingResult.Success &&
                            settingResult.Data is System.Text.Json.JsonElement el &&
                            el.ValueKind == System.Text.Json.JsonValueKind.True;

            if (!required) return (false, true);

            if (CurrentUser == null) return (true, false);

            var userResult = await Firebase.DbGetAsync($"users/{CurrentUser.Uid}");
            bool verified = userResult.Success &&
                            userResult.Data is System.Text.Json.JsonElement userData &&
                            userData.TryGetProperty("phoneVerified", out var pv) &&
                            pv.GetBoolean();

            return (true, verified);
        }
        catch (Exception ex)
        {
            Logger.Error(ex, "CheckPhoneVerificationAsync failed");
            return (false, true);
        }
    }
'''
idx = content.rfind('\n}')
content = content[:idx] + addition + content[idx:]
open(r'.\src\SionyxKiosk\Services\AuthService.cs', 'w', encoding='utf-8').write(content)
print('OK')
