path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\OrganizationMetadataService.cs'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

old = '''        var mosadId = DecodeData(SafeGet(data, "nedarim_mosad_id") ?? "");
            var apiValid = DecodeData(SafeGet(data, "nedarim_api_valid") ?? "");
            if (mosadId == null || apiValid == null)
                return Error("NEDARIM credentials not found in organization metadata");

            return Success(new
            {
                name = SafeGet(data, "name") ?? "",
                nedarim_mosad_id = mosadId,
                nedarim_api_valid = apiValid,'''

new = '''        // Read mosadId and apiPassword - stored as plain strings in Firebase.
            // SafeGetAny handles both String and Number JsonValueKind gracefully.
            static string SafeGetAny(System.Text.Json.JsonElement el, string key) {
                if (el.TryGetProperty(key, out var p))
                    return p.ValueKind == System.Text.Json.JsonValueKind.String ? p.GetString() ?? "" : p.ToString();
                return "";
            }
            var mosadId = SafeGetAny(data, "nedarim_mosad_id");
            var apiValid = SafeGetAny(data, "nedarim_api_valid");
            if (string.IsNullOrEmpty(mosadId) || string.IsNullOrEmpty(apiValid))
                return Error("NEDARIM credentials not found in organization metadata");

            return Success(new
            {
                name = SafeGet(data, "name") ?? "",
                nedarim_mosad_id = (object)mosadId,
                nedarim_api_valid = (object)apiValid,'''

count = content_n.count(old)
print(f"Found {count} matches")
if count == 1:
    content_n = content_n.replace(old, new, 1)
    open(path, 'w', encoding='utf-8', newline='\r\n').write(content_n)
    print("OK - file saved")
else:
    print("NOT FOUND - file NOT saved")
