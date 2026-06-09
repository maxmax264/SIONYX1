content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\OrganizationMetadataService.cs', encoding='utf-8').read()
old = '    public async Task<ServiceResult> GetAdminExitPasswordAsync()\n    {\n        try\n        {\n            var result = await Firebase.DbGetAsync("metadata/settings/adminExitPassword");\n            if (!result.Success || result.Data is not System.Text.Json.JsonElement el || el.ValueKind == System.Text.Json.JsonValueKind.Null)\n                return Error("not found");\n\n            var password = el.ValueKind == System.Text.Json.JsonValueKind.String ? el.GetString() : null;\n            return string.IsNullOrEmpty(password) ? Error("not found") : Success(password);\n        }\n        catch (Exception)\n        {\n            return Error("firebase error");\n        }\n    }'
new = '    public async Task<ServiceResult> GetAdminExitPasswordAsync()\n    {\n        try\n        {\n            var config = SionyxKiosk.Infrastructure.FirebaseConfig.Load();\n            using var http = new System.Net.Http.HttpClient();\n            http.Timeout = TimeSpan.FromSeconds(5);\n            var url = $"{config.DatabaseUrl}/organizations/{config.OrgId}/metadata/settings/adminExitPassword.json";\n            var response = await http.GetStringAsync(url);\n            var password = response.Trim().Trim(\'"\');\n            if (string.IsNullOrEmpty(password) || password == "null")\n                return Error("not found");\n            return Success(password);\n        }\n        catch (Exception)\n        {\n            return Error("firebase error");\n        }\n    }'
count = content.count(old)
print(f'Found: {count}')
if count == 1:
    content = content.replace(old, new)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\OrganizationMetadataService.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
