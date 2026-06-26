path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\KioskPolicyService.cs'
content = open(path, encoding='utf-8').read()

old = """    public static async System.Threading.Tasks.Task RunWithControlPanelAsync()
    {
        Remove();
        try
        {
            var psi = new ProcessStartInfo
            {
                FileName = "rundll32.exe",
                Arguments = "shell32.dll,Control_RunDLL",
                UseShellExecute = false
            };
            var process = Process.Start(psi);
            if (process != null)
            {
                await process.WaitForExitAsync();
            }
        }
        finally
        {
            Apply();
        }
    }"""

new = """    public static async System.Threading.Tasks.Task RunWithControlPanelAsync()
    {
        Remove();
        try
        {
            Process.Start(new ProcessStartInfo
            {
                FileName = "explorer.exe",
                Arguments = "shell:::{26EE0668-A00A-44D7-9371-BEB064C98683}",
                UseShellExecute = true
            });
            await System.Threading.Tasks.Task.Run(() =>
                System.Windows.MessageBox.Show(
                    "לוח הבקרה פתוח.\\nלחץ אישור לאחר שתסיים — המערכת תינעל חזרה.",
                    "SIONYX — מצב מנהל",
                    System.Windows.MessageBoxButton.OK,
                    System.Windows.MessageBoxImage.Information));
        }
        finally
        {
            Apply();
        }
    }"""

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new)
    open(path, 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("Not found")
