path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\KioskPolicyService.cs'
content = open(path, encoding='utf-8').read()

old = """    public static async System.Threading.Tasks.Task RunWithControlPanelAsync(Func<Process?> startProcess)
    {
        Remove();
        try
        {
            var process = startProcess();
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

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new)
    open(path, 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("Not found")
