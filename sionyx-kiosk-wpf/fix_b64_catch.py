path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\OrganizationMetadataService.cs'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

old = '''            static string TryDecodeBase64Json(string raw) {
                if (string.IsNullOrEmpty(raw)) return raw;
                try {
                    var bytes = Convert.FromBase64String(raw);
                    var json = System.Text.Encoding.UTF8.GetString(bytes);
                    var decoded = System.Text.Json.JsonSerializer.Deserialize<string>(json);
                    return decoded ?? raw;
                } catch { return raw; }
            }'''

new = '''            static string TryDecodeBase64Json(string raw) {
                if (string.IsNullOrEmpty(raw)) return raw;
                try {
                    var bytes = Convert.FromBase64String(raw);
                    var json = System.Text.Encoding.UTF8.GetString(bytes);
                    // Must be a valid JSON string (e.g. "\"value\"") - if Deserialize returns null
                    // or throws, the value is corrupt -> return "" so caller treats it as missing.
                    var decoded = System.Text.Json.JsonSerializer.Deserialize<string>(json);
                    return decoded ?? "";
                } catch (FormatException) {
                    // Not valid Base64 -> treat as plain string
                    return raw;
                } catch {
                    // Valid Base64 but invalid JSON string -> corrupt -> signal missing
                    return "";
                }
            }'''

count = content_n.count(old)
print(f"Found {count} matches")
if count == 1:
    content_n = content_n.replace(old, new, 1)
    open(path, 'w', encoding='utf-8', newline='\r\n').write(content_n)
    print("OK - file saved")
else:
    print("NOT FOUND - file NOT saved")
