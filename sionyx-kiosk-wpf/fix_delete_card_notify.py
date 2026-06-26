path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\PaymentDialog.xaml.cs'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

old = '''    private async Task HandleDeleteCardAsync()
    {
        try
        {
            await _firebase.DbUpdateAsync($"users/{_userId}", new Dictionary<string, object> { ["savedCard"] = null! });
            Logger.Information("Saved card deleted for user {UserId}", _userId);
        }
        catch (Exception ex)
        {
            Logger.Error(ex, "Failed to delete saved card");
        }
    }'''

new = '''    private async Task HandleDeleteCardAsync()
    {
        try
        {
            await _firebase.DbUpdateAsync($"users/{_userId}", new Dictionary<string, object> { ["savedCard"] = null! });
            Logger.Information("Saved card deleted for user {UserId}", _userId);
        }
        catch (Exception ex)
        {
            Logger.Error(ex, "Failed to delete saved card");
        }
        finally
        {
            // Notify JS regardless of outcome, so the UI doesn't stay stuck waiting for a confirmation
            // that will never come. If deletion failed, the user will simply see the iframe again
            // and can retry payment normally; savedKevaId will still be present on next dialog open
            // if the Firebase write truly failed.
            var msg = JsonSerializer.Serialize(new { action = "cardDeleted" });
            _ = Dispatcher.InvokeAsync(() => PaymentWebView.CoreWebView2.PostWebMessageAsJson(msg));
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
