import sys

path = r"src\SionyxKiosk\Services\AutoUpdateService.cs"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Add _isCheckInProgress flag
old = '    private static System.Timers.Timer? _periodicTimer = null;\n    private static string? _currentVersion = null;'
new = '    private static System.Timers.Timer? _periodicTimer = null;\n    private static string? _currentVersion = null;\n    private static volatile bool _isCheckInProgress = false;'

if old not in content:
    print("ERROR: flag target not found")
    sys.exit(1)

content = content.replace(old, new, 1)

# Guard CheckAndUpdateAsync
old2 = '    public static async Task CheckAndUpdateAsync(string currentVersion)\n    {\n        _currentVersion = currentVersion;\n        try\n        {'
new2 = '    public static async Task CheckAndUpdateAsync(string currentVersion)\n    {\n        if (_isCheckInProgress) return;\n        _isCheckInProgress = true;\n        _currentVersion = currentVersion;\n        try\n        {'

if old2 not in content:
    print("ERROR: guard target not found")
    sys.exit(1)

content = content.replace(old2, new2, 1)

# Release flag at end of CheckAndUpdateAsync - after the catch block
old3 = '''        catch (Exception ex)
        {
            Logger.Warning(ex, "[Update] Update check failed (non-fatal)");
        }

        // Start periodic timer'''
new3 = '''        catch (Exception ex)
        {
            Logger.Warning(ex, "[Update] Update check failed (non-fatal)");
        }
        finally
        {
            _isCheckInProgress = false;
        }

        // Start periodic timer'''

if old3 not in content:
    print("ERROR: finally target not found")
    sys.exit(1)

content = content.replace(old3, new3, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("AutoUpdateService patched successfully!")
