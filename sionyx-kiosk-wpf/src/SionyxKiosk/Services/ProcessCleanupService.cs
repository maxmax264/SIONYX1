using System.Diagnostics;
using System.IO;
using Serilog;

namespace SionyxKiosk.Services;

/// <summary>
/// Closes user programs when a new session starts.
/// Ensures a clean state for each customer in kiosk environments.
/// </summary>
public class ProcessCleanupService
{
    private static readonly ILogger Logger = Log.ForContext<ProcessCleanupService>();

    /// <summary>Processes that should NEVER be killed.</summary>
    private static readonly HashSet<string> Whitelist = new(StringComparer.OrdinalIgnoreCase)
    {
        // SIONYX
        "sionyxkiosk.exe", "sionyx.exe", "dotnet.exe",
        // Windows core
        "system", "smss.exe", "csrss.exe", "wininit.exe", "services.exe",
        "lsass.exe", "svchost.exe", "winlogon.exe", "explorer.exe", "dwm.exe",
        "taskhostw.exe", "sihost.exe", "ctfmon.exe", "conhost.exe",
        "fontdrvhost.exe", "audiodg.exe", "runtimebroker.exe", "searchhost.exe",
        "startmenuexperiencehost.exe", "textinputhost.exe",
        "shellexperiencehost.exe", "applicationframehost.exe",
        "systemsettings.exe", "securityhealthservice.exe",
        "securityhealthsystray.exe", "msmpeng.exe", "nissrv.exe",
        "wuauclt.exe", "trustedinstaller.exe", "tiworker.exe",
        "dllhost.exe", "msiexec.exe", "spoolsv.exe", "searchindexer.exe",
        // Drivers
        "igfxem.exe", "igfxhk.exe", "igfxtray.exe", "nvcontainer.exe",
        // Utilities
        "onedrive.exe", "settingsynchost.exe",
    };

    /// <summary>User applications to specifically target for cleanup.</summary>
    private static readonly HashSet<string> Targets = new(StringComparer.OrdinalIgnoreCase)
    {
        // Browsers
        "chrome.exe", "msedge.exe", "firefox.exe", "opera.exe", "brave.exe", "iexplore.exe",
        // Office
        "winword.exe", "excel.exe", "powerpnt.exe", "outlook.exe", "onenote.exe",
        "mspub.exe", "msaccess.exe",
        // Media
        "vlc.exe", "wmplayer.exe", "spotify.exe", "groove.exe", "itunes.exe",
        // Communication
        "teams.exe", "slack.exe", "discord.exe", "zoom.exe", "skype.exe",
        "telegram.exe", "whatsapp.exe",
        // Text editors
        "notepad.exe", "notepad++.exe", "wordpad.exe", "code.exe",
        // PDF
        "acrord32.exe", "acrobat.exe",
        // Image viewers
        "mspaint.exe",
        // Misc
        "calculator.exe", "snippingtool.exe",
    };

    /// <summary>Stubborn processes that should be killed by name.</summary>
    private static readonly HashSet<string> StubbornProcesses = new(StringComparer.OrdinalIgnoreCase)
    {
        "discord.exe", "teams.exe", "slack.exe", "zoom.exe",
    };

    /// <summary>Returns true if running in dev/test mode — skips destructive cleanup.</summary>
    private static bool IsDevMode()
    {
        var envVar = Environment.GetEnvironmentVariable("SIONYX_DEV_MODE");
        if (envVar == "1" || string.Equals(envVar, "true", StringComparison.OrdinalIgnoreCase))
            return true;
        try
        {
            using var key = Microsoft.Win32.RegistryKey.OpenBaseKey(
                Microsoft.Win32.RegistryHive.LocalMachine,
                Microsoft.Win32.RegistryView.Registry64).OpenSubKey(@"SOFTWARE\SIONYX");
            if (key?.GetValue("DevMode") is int val && val == 1)
                return true;
        }
        catch { }
        return false;
    }

    /// <summary>Close all user processes that aren't in the whitelist.</summary>
    public Dictionary<string, object> CleanupUserProcesses()
    {
        if (IsDevMode())
        {
            Logger.Information("Process cleanup skipped (DevMode)");
            return new Dictionary<string, object> { ["success"] = true, ["skipped"] = true };
        }
        Logger.Information("Starting user process cleanup for new session");

        var closedCount = 0;
        var failedCount = 0;
        var closedProcesses = new List<string>();
        var failedProcesses = new List<string>();

        var running = GetRunningProcesses();

        foreach (var (name, pids) in running)
        {
            if (Whitelist.Contains(name)) continue;
            if (!Targets.Contains(name)) continue;

            if (StubbornProcesses.Contains(name))
            {
                if (KillByName(name))
                {
                    closedCount += pids.Count;
                    if (!closedProcesses.Contains(name)) closedProcesses.Add(name);
                }
                else
                {
                    failedCount += pids.Count;
                    if (!failedProcesses.Contains(name)) failedProcesses.Add(name);
                }
            }
            else
            {
                foreach (var pid in pids)
                {
                    if (KillProcess(pid, name))
                    {
                        closedCount++;
                        if (!closedProcesses.Contains(name)) closedProcesses.Add(name);
                    }
                    else
                    {
                        failedCount++;
                        if (!failedProcesses.Contains(name)) failedProcesses.Add(name);
                    }
                }
            }
        }

        if (closedCount > 0)
            Logger.Information("Process cleanup: {Count} closed ({Processes})", closedCount, string.Join(", ", closedProcesses));
        else
            Logger.Information("No user processes found to clean up");

        return new Dictionary<string, object>
        {
            ["success"] = failedCount == 0,
            ["closed_count"] = closedCount,
            ["failed_count"] = failedCount,
            ["closed_processes"] = closedProcesses,
            ["failed_processes"] = failedProcesses,
        };
    }

    /// <summary>Close only browser processes.</summary>
    public Dictionary<string, object> CloseBrowsersOnly()
    {
        var browserNames = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        {
            "chrome.exe", "msedge.exe", "firefox.exe", "opera.exe", "brave.exe", "iexplore.exe",
        };

        var closedCount = 0;
        var running = GetRunningProcesses();

        foreach (var (name, pids) in running)
        {
            if (!browserNames.Contains(name)) continue;
            foreach (var pid in pids)
            {
                if (KillProcess(pid, name))
                    closedCount++;
            }
        }

        return new Dictionary<string, object> { ["success"] = true, ["closed_count"] = closedCount };
    }

    /// <summary>
    /// Closes every app the user opened (any process in this session with a visible window),
    /// except SIONYX itself, the shell, and remote-support tools. Also closes File Explorer windows.
    /// </summary>
    public Dictionary<string, object> CloseAllUserApps()
    {
        var closed = 0;
        try
        {
            var self = Process.GetCurrentProcess();
            var baseDir = AppContext.BaseDirectory;

            foreach (var proc in Process.GetProcesses())
            {
                try
                {
                    using (proc)
                    {
                        if (proc.Id == self.Id || proc.SessionId != self.SessionId) continue;

                        var exe = proc.ProcessName + ".exe";
                        if (Whitelist.Contains(exe) || ExtraProtected.Contains(exe)) continue;
                        if (proc.ProcessName.StartsWith("sionyx", StringComparison.OrdinalIgnoreCase)) continue;

                        // Only touch apps the user can see (background helpers stay untouched)
                        if (proc.MainWindowHandle == IntPtr.Zero) continue;

                        string? path = null;
                        try { path = proc.MainModule?.FileName; } catch { /* access denied */ }
                        if (path == null) continue; // can't identify it - leave it alone
                        if (path.StartsWith(baseDir, StringComparison.OrdinalIgnoreCase)) continue;

                        if (KillProcess(proc.Id, exe)) closed++;
                    }
                }
                catch { /* process exited meanwhile / inaccessible */ }
            }

            CloseExplorerWindows();
        }
        catch (Exception ex)
        {
            Logger.Error("CloseAllUserApps failed: {Error}", ex.Message);
        }

        return new Dictionary<string, object> { ["success"] = true, ["closed_count"] = closed };
    }

    /// <summary>Politely closes open File Explorer windows without touching explorer.exe itself.</summary>
    public static void CloseExplorerWindows()
    {
        try
        {
            EnumWindows((hWnd, _) =>
            {
                var sb = new System.Text.StringBuilder(64);
                GetClassName(hWnd, sb, sb.Capacity);
                var cls = sb.ToString();
                if (cls == "CabinetWClass" || cls == "ExploreWClass")
                    PostMessage(hWnd, 0x0010 /* WM_CLOSE */, IntPtr.Zero, IntPtr.Zero);
                return true;
            }, IntPtr.Zero);
        }
        catch (Exception ex)
        {
            Logger.Warning("CloseExplorerWindows failed: {Error}", ex.Message);
        }
    }

    /// <summary>
    /// Wipes personal folders (Documents, Pictures, Music, Videos, Recent, Temp), clears the clipboard
    /// and restores the admin-configured desktop (files, folders, wallpaper).
    /// </summary>
    public void WipeUserData()
    {
        foreach (var folder in new[]
        {
            Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments),
            Environment.GetFolderPath(Environment.SpecialFolder.MyPictures),
            Environment.GetFolderPath(Environment.SpecialFolder.MyMusic),
            Environment.GetFolderPath(Environment.SpecialFolder.MyVideos),
            Environment.GetFolderPath(Environment.SpecialFolder.Recent),
        })
            EmptyFolder(folder, skipRecent: false);

        EmptyFolder(Path.GetTempPath(), skipRecent: true);
        ClearClipboard();

        try { new DesktopSnapshotService().RestoreSnapshot(); }
        catch (Exception ex) { Logger.Error("Desktop restore failed: {Error}", ex.Message); }
    }

    private static void EmptyFolder(string folder, bool skipRecent)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(folder) || !Directory.Exists(folder)) return;
            // Safety: never touch cloud-synced folders or anything outside the user profile / temp
            if (folder.Contains("OneDrive", StringComparison.OrdinalIgnoreCase)) return;
            var profile = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
            var temp = Path.GetTempPath();
            if (!folder.StartsWith(profile, StringComparison.OrdinalIgnoreCase) &&
                !folder.StartsWith(temp, StringComparison.OrdinalIgnoreCase)) return;
            if (string.Equals(folder.TrimEnd('\\'), profile.TrimEnd('\\'), StringComparison.OrdinalIgnoreCase)) return;

            var cutoff = DateTime.Now.AddMinutes(-1);
            foreach (var entry in new DirectoryInfo(folder).EnumerateFileSystemInfos())
            {
                try
                {
                    if (skipRecent && entry.LastWriteTime > cutoff) continue;
                    if (entry.Name.StartsWith("sionyx", StringComparison.OrdinalIgnoreCase)) continue;
                    if (entry is DirectoryInfo d) d.Delete(recursive: true);
                    else entry.Delete();
                }
                catch { /* in use - skip */ }
            }
        }
        catch (Exception ex)
        {
            Logger.Warning("EmptyFolder {Folder} failed: {Error}", folder, ex.Message);
        }
    }

    private static void ClearClipboard()
    {
        try
        {
            var dispatcher = System.Windows.Application.Current?.Dispatcher;
            if (dispatcher == null) return;
            dispatcher.Invoke(() =>
            {
                for (var i = 0; i < 3; i++)
                {
                    try { System.Windows.Clipboard.Clear(); break; }
                    catch { Thread.Sleep(100); }
                }
            });
        }
        catch (Exception ex)
        {
            Logger.Warning("ClearClipboard failed: {Error}", ex.Message);
        }
    }

    private static readonly HashSet<string> ExtraProtected = new(StringComparer.OrdinalIgnoreCase)
    {
        "anydesk.exe", "aeroadmin.exe", "tvnserver.exe", "winvnc.exe", "rustdesk.exe",
        "osk.exe", "tabtip.exe", "searchapp.exe", "searchhost.exe", "widgets.exe", "lockapp.exe",
        "startmenuexperiencehost.exe", "shellexperiencehost.exe", "textinputhost.exe",
    };

    private delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
    [System.Runtime.InteropServices.DllImport("user32.dll")]
    private static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
    [System.Runtime.InteropServices.DllImport("user32.dll", CharSet = System.Runtime.InteropServices.CharSet.Auto)]
    private static extern int GetClassName(IntPtr hWnd, System.Text.StringBuilder lpClassName, int nMaxCount);
    [System.Runtime.InteropServices.DllImport("user32.dll")]
    private static extern bool PostMessage(IntPtr hWnd, uint msg, IntPtr wParam, IntPtr lParam);

    // ==================== PRIVATE ====================

    private static Dictionary<string, List<int>> GetRunningProcesses()
    {
        var processes = new Dictionary<string, List<int>>(StringComparer.OrdinalIgnoreCase);

        try
        {
            var si = new ProcessStartInfo
            {
                FileName = "tasklist",
                Arguments = "/FO CSV /NH",
                CreateNoWindow = true,
                UseShellExecute = false,
                RedirectStandardOutput = true,
            };

            using var proc = Process.Start(si);
            var output = proc?.StandardOutput.ReadToEnd() ?? "";
            proc?.WaitForExit(10000);

            foreach (var line in output.Split('\n', StringSplitOptions.RemoveEmptyEntries))
            {
                var parts = line.Split(',');
                if (parts.Length < 2) continue;
                var name = parts[0].Trim('"', ' ');
                if (int.TryParse(parts[1].Trim('"', ' '), out var pid))
                {
                    if (!processes.ContainsKey(name))
                        processes[name] = new List<int>();
                    processes[name].Add(pid);
                }
            }
        }
        catch (Exception ex)
        {
            Logger.Error("Error getting process list: {Error}", ex.Message);
        }

        return processes;
    }

    private static bool KillProcess(int pid, string name, int retryCount = 2)
    {
        for (var attempt = 0; attempt <= retryCount; attempt++)
        {
            try
            {
                var si = new ProcessStartInfo
                {
                    FileName = "taskkill",
                    Arguments = $"/PID {pid} /F /T",
                    CreateNoWindow = true,
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                };

                using var proc = Process.Start(si);
                proc?.WaitForExit(5000);

                if (proc?.ExitCode == 0) return true;

                var stderr = proc?.StandardError.ReadToEnd() ?? "";
                if (stderr.Contains("not found", StringComparison.OrdinalIgnoreCase)) return true;

                if (attempt < retryCount)
                    Thread.Sleep(200);
            }
            catch (Exception ex)
            {
                Logger.Error("Error killing process {Name}: {Error}", name, ex.Message);
                return false;
            }
        }
        return false;
    }

    private static bool KillByName(string processName)
    {
        try
        {
            var si = new ProcessStartInfo
            {
                FileName = "taskkill",
                Arguments = $"/IM {processName} /F /T",
                CreateNoWindow = true,
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
            };

            using var proc = Process.Start(si);
            proc?.WaitForExit(10000);

            if (proc?.ExitCode == 0) return true;
            var stderr = proc?.StandardError.ReadToEnd() ?? "";
            return stderr.Contains("not found", StringComparison.OrdinalIgnoreCase);
        }
        catch (Exception ex)
        {
            Logger.Error("Error killing by name {Name}: {Error}", processName, ex.Message);
            return false;
        }
    }
}
