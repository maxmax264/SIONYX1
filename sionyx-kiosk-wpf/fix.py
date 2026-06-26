content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\PaymentDialog.xaml.cs', encoding='utf-8').read()

old = '''    private async Task<bool> InstallWebView2Async()
    {
        try
        {
            var installerPath = Path.Combine(Path.GetTempPath(), "MicrosoftEdgeWebview2Setup.exe");

            Logger.Information("Downloading WebView2 bootstrapper...");
            using var httpClient = new HttpClient();
            httpClient.Timeout = TimeSpan.FromMinutes(3);
            var bytes = await httpClient.GetByteArrayAsync(
                "https://go.microsoft.com/fwlink/p/?LinkId=2124703");
            await File.WriteAllBytesAsync(installerPath, bytes);

            Logger.Information("Installing WebView2...");
            var process = System.Diagnostics.Process.Start(
                new System.Diagnostics.ProcessStartInfo
                {
                    FileName = installerPath,
                    Arguments = "/silent /install",
                    UseShellExecute = true,
                    Verb = "runas"   // UAC — required for system-level install
                });

            if (process == null)
            {
                Logger.Error("Failed to start WebView2 installer process");
                return false;
            }

            await process.WaitForExitAsync();
            Logger.Information("WebView2 installer exit code: {Code}", process.ExitCode);
            return process.ExitCode == 0;
        }
        catch (Exception ex)
        {
            Logger.Error(ex, "Failed to install WebView2");
            return false;
        }
    }'''

new = '''    private async Task<bool> InstallWebView2Async()
    {
        try
        {
            // Use unique filename to avoid file-lock conflicts on retry
            var installerPath = Path.Combine(
                Path.GetTempPath(),
                $"MicrosoftEdgeWebview2Setup_{Guid.NewGuid():N}.exe");

            Logger.Information("Downloading WebView2 bootstrapper to {Path}...", installerPath);
            using var httpClient = new HttpClient();
            httpClient.Timeout = TimeSpan.FromMinutes(3);
            var bytes = await httpClient.GetByteArrayAsync(
                "https://go.microsoft.com/fwlink/p/?LinkId=2124703");
            await File.WriteAllBytesAsync(installerPath, bytes);

            Logger.Information("Installing WebView2...");
            var process = System.Diagnostics.Process.Start(
                new System.Diagnostics.ProcessStartInfo
                {
                    FileName = installerPath,
                    Arguments = "/silent /install",
                    UseShellExecute = true,
                    Verb = "runas"
                });

            if (process == null)
            {
                Logger.Error("Failed to start WebView2 installer process");
                return false;
            }

            await process.WaitForExitAsync();
            Logger.Information("WebView2 installer exit code: {Code}", process.ExitCode);

            // Give the runtime a moment to register after install
            await Task.Delay(TimeSpan.FromSeconds(2));

            // Clean up installer
            try { File.Delete(installerPath); } catch { }

            // Exit code 0 = success, 3010 = success + reboot needed
            return process.ExitCode is 0 or 3010;
        }
        catch (Exception ex)
        {
            Logger.Error(ex, "Failed to install WebView2");
            return false;
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
