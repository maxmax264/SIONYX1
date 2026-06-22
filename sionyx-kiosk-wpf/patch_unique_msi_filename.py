path = r"src\SionyxKiosk\Services\AutoUpdateService.cs"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

changes = 0

# ---------------------------------------------------------------------------
# Fix: unique MSI filename per download attempt.
#
# Previously every download attempt for the same version wrote to the exact
# same path (sionyx_update_{version}.msi). When the periodic timer fired
# again before the scheduled task had finished reading/installing the
# previous file, a new download would overwrite that file while msiexec was
# still trying to open it for reading -> MSI error 1619/2203
# (ERROR_INSTALL_PACKAGE_OPEN_FAILED), which fails silently under /quiet.
#
# Giving each attempt a unique filename (version + UTC ticks) means an old
# attempt's file is never overwritten or deleted by a newer attempt, so
# msiexec can always finish reading whichever file it was pointed at via the
# trigger file.
# ---------------------------------------------------------------------------

old_a = 'var tempPath = Path.Combine(GetUpdateFolder(), $"sionyx_update_{version}.msi");'
new_a = 'var tempPath = Path.Combine(GetUpdateFolder(), $"sionyx_update_{version}_{DateTime.UtcNow.Ticks}.msi");'

count_a = content.count(old_a)
if count_a == 1:
    content = content.replace(old_a, new_a)
    changes += 1
    print("Applied: unique filename in DownloadInBackgroundAsync.")
else:
    print(f"NOT applied (DownloadInBackgroundAsync): found {count_a} occurrences, expected 1.")

old_b = 'var tempPath = Path.Combine(GetUpdateFolder(), $"sionyx_update_{newVersion}.msi");'
new_b = 'var tempPath = Path.Combine(GetUpdateFolder(), $"sionyx_update_{newVersion}_{DateTime.UtcNow.Ticks}.msi");'

count_b = content.count(old_b)
if count_b == 1:
    content = content.replace(old_b, new_b)
    changes += 1
    print("Applied: unique filename in DownloadAndInstallAsync.")
else:
    print(f"NOT applied (DownloadAndInstallAsync): found {count_b} occurrences, expected 1.")

# ---------------------------------------------------------------------------
# Also: clean up old leftover MSI files in the update folder before starting
# a new download, so the folder does not accumulate stale multi-hundred-MB
# files forever across many install attempts. We only delete .msi files
# (never the live pending_update.txt) and only ones older than 10 minutes,
# so we never touch a file that might still be mid-install.
# ---------------------------------------------------------------------------
anchor = '''    private static string GetUpdateFolder()
    {
        var folder = Path.Combine(@"C:\\Users\\Public\\Documents\\SIONYX", "updates");
        Directory.CreateDirectory(folder);
        return folder;
    }'''

new_anchor = '''    private static string GetUpdateFolder()
    {
        var folder = Path.Combine(@"C:\\Users\\Public\\Documents\\SIONYX", "updates");
        Directory.CreateDirectory(folder);
        CleanupOldMsiFiles(folder);
        return folder;
    }

    /// <summary>
    /// Deletes leftover .msi files older than 10 minutes from the update
    /// folder. Each download now uses a unique filename (version + ticks),
    /// so without this cleanup the folder would accumulate a new ~67MB file
    /// on every install attempt forever. Files newer than 10 minutes are
    /// left alone in case a scheduled task run is still reading one.
    /// </summary>
    private static void CleanupOldMsiFiles(string folder)
    {
        try
        {
            foreach (var file in Directory.GetFiles(folder, "sionyx_update_*.msi"))
            {
                try
                {
                    var info = new FileInfo(file);
                    if (DateTime.UtcNow - info.LastWriteTimeUtc > TimeSpan.FromMinutes(10))
                        info.Delete();
                }
                catch
                {
                    // File may be in use by msiexec right now; skip it silently,
                    // it will be picked up by a later cleanup pass.
                }
            }
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "[Update] Could not clean up old MSI files");
        }
    }'''

count_anchor = content.count(anchor)
if count_anchor == 1:
    content = content.replace(anchor, new_anchor)
    changes += 1
    print("Applied: old MSI cleanup helper added.")
else:
    print(f"NOT applied (cleanup helper): found {count_anchor} occurrences, expected 1.")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\nTotal changes applied: {changes} of 3 expected.")
