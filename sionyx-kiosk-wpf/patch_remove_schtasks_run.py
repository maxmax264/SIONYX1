import sys

path = r"src\SionyxKiosk\Services\AutoUpdateService.cs"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = '''    private static bool TryRunViaScheduledTask(string msiPath)
    {
        try
        {
            var triggerFile = Path.Combine(@"C:\\Windows\\Temp", "pending_update.txt");
            File.WriteAllText(triggerFile, msiPath);
            var psi = new ProcessStartInfo
            {
                FileName = "schtasks.exe",
                Arguments = "/run /tn \\"SIONYX_Update\\"",
                UseShellExecute = false,
                CreateNoWindow = true
            };
            var proc = Process.Start(psi);
            proc?.WaitForExit(5000);
            return proc?.ExitCode == 0;
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "[Update] Could not run scheduled task");
            return false;
        }
    }'''

new = '''    private static bool TryRunViaScheduledTask(string msiPath)
    {
        try
        {
            // Write trigger file to C:\\Windows\\Temp — SIONYX_Update scheduled task
            // runs every minute as SYSTEM and picks it up automatically
            var triggerFile = Path.Combine(@"C:\\Windows\\Temp", "pending_update.txt");
            File.WriteAllText(triggerFile, msiPath);
            Logger.Information("[Update] Trigger file written — waiting for scheduled task to pick up");
            return true;
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "[Update] Could not write trigger file");
            return false;
        }
    }'''

if old not in content:
    # Try to find it differently
    print("Trying alternate search...")
    idx = content.find("private static bool TryRunViaScheduledTask")
    if idx == -1:
        print("ERROR: Method not found at all.")
        sys.exit(1)
    print(f"Found at index {idx}, showing context:")
    print(repr(content[idx:idx+500]))
    sys.exit(1)

content = content.replace(old, new, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched successfully!")
