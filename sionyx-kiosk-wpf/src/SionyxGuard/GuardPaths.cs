namespace SionyxGuard;

/// <summary>File contract shared with SionyxKiosk's GuardBeacon (keep both in sync).</summary>
internal static class GuardPaths
{
    public static readonly string Dir = @"C:\ProgramData\SIONYX\guard";
    public static readonly string Beat = Path.Combine(Dir, "app.beat");
    public static readonly string CleanExit = Path.Combine(Dir, "app.clean");
    public static readonly string LockFlag = Path.Combine(Dir, "lock.flag");
    public const string DisableKey = @"SOFTWARE\SIONYX\Guard";
    public const string DisableValue = "Disabled";
}
