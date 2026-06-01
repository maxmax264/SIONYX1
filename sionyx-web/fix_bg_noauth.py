f = open(r'.\src\SionyxKiosk\Services\OrganizationMetadataService.cs', encoding='utf-8')
c = f.read()
f.close()

old = '''    public async Task<ServiceResult> GetKioskBackgroundAsync()
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
    }'''

new = '''    public async Task<ServiceResult> GetKioskBackgroundAsync()
    {
        try
        {
            var config = SionyxKiosk.Infrastructure.FirebaseConfig.Load();
            var url = $"{config.DatabaseUrl}/organizations/{config.OrgId}/metadata.json";
            using var http = new System.Net.Http.HttpClient();
            var json = await http.GetStringAsync(url);
            var data = System.Text.Json.JsonSerializer.Deserialize<System.Text.Json.JsonElement>(json);
            if (data.ValueKind == System.Text.Json.JsonValueKind.Null)
                return Success(new { enabled = false, url = "" });
            var enabled = data.TryGetProperty("kioskBackgroundEnabled", out var en) && en.GetBoolean();
            var bgUrl = SafeGet(data, "kioskBackgroundUrl") ?? "";
            return Success(new { enabled, url = bgUrl });
        }
        catch (Exception ex)
        {
            return Error(HandleFirebaseError(ex, "GetKioskBackground"));
        }
    }'''

assert c.count(old) == 1
c = c.replace(old, new, 1)
open(r'.\src\SionyxKiosk\Services\OrganizationMetadataService.cs', 'w', encoding='utf-8').write(c)
print("OK")
