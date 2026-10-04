using System.IO;
using Microsoft.Win32;
using Serilog;

namespace SionyxKiosk.Services;

/// <summary>
/// Saves and restores the SionyxUser desktop state.
/// Admin configures the desktop, saves a snapshot, and every new client session restores it.
/// </summary>
public class DesktopSnapshotService
{
    private static readonly ILogger Logger = Log.ForContext<DesktopSnapshotService>();

    // Was hardcoded to "C:\Users\SionyxUser\Desktop" - broke with DirectoryNotFoundException
    // on any kiosk whose local account isn't literally named "SionyxUser" (or whose Desktop
    // is redirected, e.g. via OneDrive). Resolve the actual desktop of whichever account the
    // kiosk app is running as instead.
    private static string DesktopPath => Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory);
    private const string SnapshotPath = @"C:\Users\Public\Documents\SIONYX\DesktopSnapshot";
    private const string WallpaperRegistryKey = @"Control Panel\Desktop";
    private const string WallpaperRegistryValue = "Wallpaper";
    private const string WallpaperSnapshotFile = "__wallpaper_path.txt";

    /// <summary>
    /// Called when admin clicks "???? ?????".
    /// Copies current desktop + wallpaper path into snapshot folder.
    /// </summary>
    public void SaveSnapshot()
    {
        Logger.Information("[Snapshot] Saving desktop snapshot...");

        try
        {
            // Clear old snapshot
            if (Directory.Exists(SnapshotPath))
                Directory.Delete(SnapshotPath, recursive: true);
            Directory.CreateDirectory(SnapshotPath);

            // Copy everything on the desktop (files AND folders, recursively)
            if (!Directory.Exists(DesktopPath))
                Directory.CreateDirectory(DesktopPath);
            var copied = CopyDirectoryContents(DesktopPath, SnapshotPath);

            // Save wallpaper path
            var wallpaper = Registry.CurrentUser
                .OpenSubKey(WallpaperRegistryKey)
                ?.GetValue(WallpaperRegistryValue) as string ?? "";
            File.WriteAllText(Path.Combine(SnapshotPath, WallpaperSnapshotFile), wallpaper);

            Logger.Information("[Snapshot] Saved {Count} items, wallpaper: {Wallpaper}", copied, wallpaper);
        }
        catch (Exception ex)
        {
            Logger.Error(ex, "[Snapshot] Failed to save snapshot");
        }
    }

    /// <summary>
    /// Called on every new client session start.
    /// Restores desktop from snapshot, removes anything the previous client added.
    /// </summary>
    public void RestoreSnapshot()
    {
        Logger.Information("[Snapshot] Restoring desktop snapshot...");

        if (!Directory.Exists(SnapshotPath))
        {
            Logger.Warning("[Snapshot] No snapshot found, skipping restore");
            return;
        }

        try
        {
            // Desktop folder can legitimately be missing (fresh/never-used Windows profile) -
            // create it instead of letting GetFiles throw and aborting the whole restore
            // (including the wallpaper restore below).
            if (!Directory.Exists(DesktopPath))
                Directory.CreateDirectory(DesktopPath);

            // Remove all files currently on desktop
            foreach (var file in Directory.GetFiles(DesktopPath, "*", SearchOption.TopDirectoryOnly))
            {
                try { File.Delete(file); }
                catch (Exception ex) { Logger.Warning("[Snapshot] Could not delete {File}: {Err}", file, ex.Message); }
            }

            // Remove all directories currently on desktop
            foreach (var dir in Directory.GetDirectories(DesktopPath))
            {
                try { Directory.Delete(dir, recursive: true); }
                catch (Exception ex) { Logger.Warning("[Snapshot] Could not delete dir {Dir}: {Err}", dir, ex.Message); }
            }

            // Restore files AND folders from snapshot (skip internal snapshot files)
            var restored = CopyDirectoryContents(SnapshotPath, DesktopPath, skipTopLevelName: WallpaperSnapshotFile);

            // Restore wallpaper
            var wallpaperFile = Path.Combine(SnapshotPath, WallpaperSnapshotFile);
            if (File.Exists(wallpaperFile))
            {
                var wallpaper = File.ReadAllText(wallpaperFile).Trim();
                if (!string.IsNullOrEmpty(wallpaper) && File.Exists(wallpaper))
                {
                    Registry.CurrentUser
                        .OpenSubKey(WallpaperRegistryKey, writable: true)
                        ?.SetValue(WallpaperRegistryValue, wallpaper);

                    // Force Windows to refresh wallpaper
                    SystemParametersInfo(20, 0, wallpaper, 0x01 | 0x02);
                    Logger.Information("[Snapshot] Wallpaper restored: {Wallpaper}", wallpaper);
                }
            }

            Logger.Information("[Snapshot] Restored {Count} items", restored);

            // Make Explorer redraw the desktop right away (otherwise removed icons can linger until refresh)
            SHChangeNotify(0x08000000 /* SHCNE_ASSOCCHANGED */, 0, IntPtr.Zero, IntPtr.Zero);
        }
        catch (Exception ex)
        {
            Logger.Error(ex, "[Snapshot] Failed to restore snapshot");
        }
    }

    public bool SnapshotExists() => Directory.Exists(SnapshotPath) &&
        (Directory.GetFiles(SnapshotPath).Any(f => Path.GetFileName(f) != WallpaperSnapshotFile)
         || Directory.GetDirectories(SnapshotPath).Length > 0);

    /// <summary>Recursively copies files and folders from src into dst. Returns number of items copied.</summary>
    private static int CopyDirectoryContents(string src, string dst, string? skipTopLevelName = null)
    {
        Directory.CreateDirectory(dst);
        var count = 0;
        foreach (var file in Directory.GetFiles(src))
        {
            var name = Path.GetFileName(file);
            if (skipTopLevelName != null && name == skipTopLevelName) continue;
            try { File.Copy(file, Path.Combine(dst, name), overwrite: true); count++; }
            catch (Exception ex) { Logger.Warning("[Snapshot] Could not copy {File}: {Err}", file, ex.Message); }
        }
        foreach (var dir in Directory.GetDirectories(src))
        {
            try { count += 1 + CopyDirectoryContents(dir, Path.Combine(dst, Path.GetFileName(dir))); }
            catch (Exception ex) { Logger.Warning("[Snapshot] Could not copy dir {Dir}: {Err}", dir, ex.Message); }
        }
        return count;
    }

    [System.Runtime.InteropServices.DllImport("shell32.dll")]
    private static extern void SHChangeNotify(int wEventId, uint uFlags, IntPtr dwItem1, IntPtr dwItem2);

    [System.Runtime.InteropServices.DllImport("user32.dll", CharSet = System.Runtime.InteropServices.CharSet.Auto)]
    private static extern int SystemParametersInfo(int uAction, int uParam, string lpvParam, int fuWinIni);
}
