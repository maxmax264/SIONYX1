path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\PaymentDialog.xaml.cs'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

old = '''            if (metaResult.IsSuccess && metaResult.Data != null)
            {
                var dt = metaResult.Data.GetType();
                if (dt.GetProperty("nedarim_mosad_id")?.GetValue(metaResult.Data) is JsonElement mosadEl)
                    mosadId = mosadEl.ValueKind == System.Text.Json.JsonValueKind.String ? mosadEl.GetString() ?? "" : mosadEl.ToString();
                if (dt.GetProperty("nedarim_api_valid")?.GetValue(metaResult.Data) is JsonElement apiEl)
                    apiPassword = apiEl.ValueKind == System.Text.Json.JsonValueKind.String ? apiEl.GetString() ?? "" : apiEl.ToString();
            }'''

new = '''            if (metaResult.IsSuccess && metaResult.Data != null)
            {
                var dt = metaResult.Data.GetType();
                // nedarim_mosad_id and nedarim_api_valid are returned as plain strings (object)
                var mosadProp = dt.GetProperty("nedarim_mosad_id")?.GetValue(metaResult.Data);
                var apiProp   = dt.GetProperty("nedarim_api_valid")?.GetValue(metaResult.Data);
                if (mosadProp is JsonElement mosadEl)
                    mosadId = mosadEl.ValueKind == System.Text.Json.JsonValueKind.String ? mosadEl.GetString() ?? "" : mosadEl.ToString();
                else if (mosadProp is string mosadStr)
                    mosadId = mosadStr;
                if (apiProp is JsonElement apiEl)
                    apiPassword = apiEl.ValueKind == System.Text.Json.JsonValueKind.String ? apiEl.GetString() ?? "" : apiEl.ToString();
                else if (apiProp is string apiStr)
                    apiPassword = apiStr;
            }'''

count = content_n.count(old)
print(f"Found {count} matches")
if count == 1:
    content_n = content_n.replace(old, new, 1)
    open(path, 'w', encoding='utf-8', newline='\r\n').write(content_n)
    print("OK - file saved")
else:
    print("NOT FOUND - file NOT saved")
