content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\KioskPolicyService.cs', encoding='utf-8').read()

old = """    public static void RunWithControlPanel(Action action)
    {
        Remove();
        try { action(); }
        finally { Apply(); }
    }"""

new = """    public static void RunWithControlPanel(Action action)
    {
        Remove();
        try { action(); }
        finally { Apply(); }
    }

    public static async System.Threading.Tasks.Task RunWithControlPanelAsync(Func<Process?> startProcess)
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

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\KioskPolicyService.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print("Not found")
