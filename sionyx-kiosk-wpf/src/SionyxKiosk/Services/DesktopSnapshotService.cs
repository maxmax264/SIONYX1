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

    private const string DesktopPath = @"C:\Users\SionyxUser\Desktop";
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

            // Copy all desktop files
            var copied = 0;
            foreach (var file in Directory.GetFiles(DesktopPath, "*", SearchOption.TopDirectoryOnly))
            {
                var dest = Path.Combine(SnapshotPath, Path.GetFileName(file));
                File.Copy(file, dest, overwrite: true);
                copied++;
            }

            // Save wallpaper path
            var wallpaper = Registry.CurrentUser
                .OpenSubKey(WallpaperRegistryKey)
                ?.GetValue(WallpaperRegistryValue) as string ?? "";
            File.WriteAllText(Path.Combine(SnapshotPath, WallpaperSnapshotFile), wallpaper);

            Logger.Information("[Snapshot] Saved {Count} files, wallpaper: {Wallpaper}", copied, wallpaper);
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

            // Restore files from snapshot (skip internal snapshot files)
            var restored = 0;
            foreach (var file in Directory.GetFiles(SnapshotPath, "*", SearchOption.TopDirectoryOnly))
            {
                var fileName = Path.GetFileName(file);
                if (fileName == WallpaperSnapshotFile) continue;

                var dest = Path.Combine(DesktopPath, fileName);
                File.Copy(file, dest, overwrite: true);
                restored++;
            }

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

            Logger.Information("[Snapshot] Restored {Count} files", restored);
        }
        catch (Exception ex)
        {
            Logger.Error(ex, "[Snapshot] Failed to restore snapshot");
        }
    }

    public bool SnapshotExists() => Directory.Exists(SnapshotPath) &&
        Directory.GetFiles(SnapshotPath).Any(f => Path.GetFileName(f) != WallpaperSnapshotFile);

    [System.Runtime.InteropServices.DllImport("user32.dll", CharSet = System.Runtime.InteropServices.CharSet.Auto)]
    private static extern int SystemParametersInfo(int uAction, int uParam, string lpvParam, int fuWinIni);
}
