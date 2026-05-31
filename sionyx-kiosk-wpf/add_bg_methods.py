# 1. הוסף מתודה ל-OrganizationMetadataService
f = open(r'.\src\SionyxKiosk\Services\OrganizationMetadataService.cs', encoding='utf-8')
c = f.read()
f.close()

old = '    public async Task<ServiceResult> GetAdminContactAsync()'
new = '''    public async Task<ServiceResult> GetKioskBackgroundAsync()
    {
        try
        {
            var result = await Firebase.DbGetAsync("metadata");
            if (!result.Success || result.Data is not System.Text.Json.JsonElement data || data.ValueKind == System.Text.Json.JsonValueKind.Null)
                return Success(new { enabled = false, url = "" });

            var enabled = data.TryGetProperty("kioskBackgroundEnabled", out var en) && en.GetBoolean();
            var url = SafeGet(data, "kioskBackgroundUrl") ?? "";
            return Success(new { enabled, url });
        }
        catch (Exception ex)
        {
            return Error(HandleFirebaseError(ex, "GetKioskBackground"));
        }
    }

    public async Task<ServiceResult> GetAdminContactAsync()'''

assert c.count(old) == 1
c = c.replace(old, new, 1)
open(r'.\src\SionyxKiosk\Services\OrganizationMetadataService.cs', 'w', encoding='utf-8').write(c)
print("OrganizationMetadataService OK")

# 2. תקן את AuthViewModel - החלף את LoadBackgroundAsync
f = open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8')
c = f.read()
f.close()

old2 = '''    private async Task LoadBackgroundAsync()
    {
        try
        {
            var db = SionyxKiosk.Infrastructure.FirebaseConfig.Database;
            var orgId = SionyxKiosk.Infrastructure.FirebaseConfig.OrgId;
            var snap = await db.Child($"organizations/{orgId}/metadata").OnceSingleAsync<System.Collections.Generic.Dictionary<string, object>>();
            if (snap != null
                && snap.TryGetValue("kioskBackgroundEnabled", out var en) && en is bool enabled && enabled
                && snap.TryGetValue("kioskBackgroundUrl", out var url) && url is string urlStr && !string.IsNullOrWhiteSpace(urlStr))
            {
                BackgroundImageUrl = urlStr;
                HasBackgroundImage = true;
            }
            else
            {
                BackgroundImageUrl = "";
                HasBackgroundImage = false;
            }
        }
        catch
        {
            BackgroundImageUrl = "";
            HasBackgroundImage = false;
        }
    }'''

new2 = '''    private async Task LoadBackgroundAsync()
    {
        if (_metadataService == null) return;
        try
        {
            var result = await _metadataService.GetKioskBackgroundAsync();
            if (result.IsSuccess && result.Data is { } data)
            {
                var type = data.GetType();
                var enabled = type.GetProperty("enabled")?.GetValue(data) is bool b && b;
                var url = type.GetProperty("url")?.GetValue(data)?.ToString() ?? "";
                if (enabled && !string.IsNullOrWhiteSpace(url))
                {
                    BackgroundImageUrl = url;
                    HasBackgroundImage = true;
                    return;
                }
            }
        }
        catch { }
        BackgroundImageUrl = "";
        HasBackgroundImage = false;
    }'''

assert c.count(old2) == 1
c = c.replace(old2, new2, 1)

# הסר את using System.Net.Http שלא צריך
c = c.replace('using System.Net.Http;\n', '')

open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', 'w', encoding='utf-8').write(c)
print("AuthViewModel OK")
