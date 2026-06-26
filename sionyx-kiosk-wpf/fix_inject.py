content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\PaymentDialog.xaml.cs', encoding='utf-8').read()

old = '''    private async Task InjectConfigAsync()
    {
        try
        {
            var metaResult = await _metadataService.GetOrganizationMetadataAsync(_firebase.OrgId);
            var mosadId = "";
            var apiValid = "";

            if (metaResult.IsSuccess && metaResult.Data != null)
            {
                var dataType = metaResult.Data.GetType();

                if (dataType.GetProperty("nedarim_mosad_id")?.GetValue(metaResult.Data) is JsonElement mosadEl)
                    mosadId = mosadEl.ValueKind == JsonValueKind.String ? mosadEl.GetString() ?? "" : mosadEl.ToString();

                if (dataType.GetProperty("nedarim_api_valid")?.GetValue(metaResult.Data) is JsonElement apiEl)
                    apiValid = apiEl.ValueKind == JsonValueKind.String ? apiEl.GetString() ?? "" : apiEl.ToString();
            }

            if (string.IsNullOrEmpty(mosadId) || string.IsNullOrEmpty(apiValid))
                Logger.Warning("Nedarim credentials missing — payment will fail");

            var callbackUrl = $"https://us-central1-{_firebase.ProjectId}.cloudfunctions.net/nedarimCallback";

            var config = new
            {
                mosadId,
                apiValid,
                amount = _package.DisplayPrice.ToString("F0"),
                packageName = _package.Name ?? "",
                packageMinutes = _package.Minutes.ToString(),
                packagePrints = _package.Prints.ToString(),
                userName = "",
                orgId = _firebase.OrgId,
                callbackUrl
            };

            var message = JsonSerializer.Serialize(new { action = "setConfig", config });
            PaymentWebView.CoreWebView2.PostWebMessageAsJson(message);

            Logger.Information("Payment config injected for package: {Package} amount: {Amount}",
                _package.Name, _package.DisplayPrice);
        }
        catch (Exception ex)
        {
            Logger.Error(ex, "Failed to inject payment config");
        }
    }'''

new = '''    private async Task InjectConfigAsync()
    {
        try
        {
            var metaResult = await _metadataService.GetOrganizationMetadataAsync(_firebase.OrgId);
            var mosadId = "";
            var apiValid = "";

            if (metaResult.IsSuccess && metaResult.Data != null)
            {
                var dataType = metaResult.Data.GetType();

                if (dataType.GetProperty("nedarim_mosad_id")?.GetValue(metaResult.Data) is JsonElement mosadEl)
                    mosadId = mosadEl.ValueKind == JsonValueKind.String ? mosadEl.GetString() ?? "" : mosadEl.ToString();

                if (dataType.GetProperty("nedarim_api_valid")?.GetValue(metaResult.Data) is JsonElement apiEl)
                    apiValid = apiEl.ValueKind == JsonValueKind.String ? apiEl.GetString() ?? "" : apiEl.ToString();
            }

            if (string.IsNullOrEmpty(mosadId) || string.IsNullOrEmpty(apiValid))
                Logger.Warning("Nedarim credentials missing — payment will fail");

            // Read payment settings (save card feature)
            var saveCardEnabled = false;
            var saveCardApiValid = "";
            var paymentSettingsResult = await _firebase.DbGetAsync("metadata/settings/payment");
            if (paymentSettingsResult.Success && paymentSettingsResult.Data is JsonElement paymentData
                && paymentData.ValueKind == JsonValueKind.Object)
            {
                saveCardEnabled = paymentData.TryGetProperty("saveCardEnabled", out var sce) && sce.GetBoolean();
                saveCardApiValid = paymentData.TryGetProperty("nedarimApiValid", out var scav)
                    ? scav.GetString() ?? "" : "";
            }
            Logger.Information("Payment settings: saveCard={SaveCard}", saveCardEnabled);

            var callbackUrl = $"https://us-central1-{_firebase.ProjectId}.cloudfunctions.net/nedarimCallback";

            var config = new
            {
                mosadId,
                apiValid,
                amount = _package.DisplayPrice.ToString("F0"),
                packageName = _package.Name ?? "",
                packageMinutes = _package.Minutes.ToString(),
                packagePrints = _package.Prints.ToString(),
                userName = "",
                orgId = _firebase.OrgId,
                callbackUrl,
                saveCardEnabled,
                saveCardApiValid
            };

            var message = JsonSerializer.Serialize(new { action = "setConfig", config });
            PaymentWebView.CoreWebView2.PostWebMessageAsJson(message);

            Logger.Information("Payment config injected for package: {Package} amount: {Amount}",
                _package.Name, _package.DisplayPrice);
        }
        catch (Exception ex)
        {
            Logger.Error(ex, "Failed to inject payment config");
        }
    }'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\PaymentDialog.xaml.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
