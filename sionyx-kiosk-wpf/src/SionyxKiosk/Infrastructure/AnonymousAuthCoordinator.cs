using Microsoft.Win32;
using Serilog;

namespace SionyxKiosk.Infrastructure;

/// <summary>
/// Process-wide coordination of Firebase anonymous sign-in.
/// Several services (heartbeat, remote command, VNC relay, ServerResolver)
/// each own a FirebaseClient and used to call signUp independently, every
/// 30s on failure. Firebase rate-limits signUp per IP
/// (TOO_MANY_ATTEMPTS_TRY_LATER), and a whole room of kiosks shares one IP,
/// so a mass restart (e.g. an update) blocked them all for ~10 minutes.
/// This class gives them: one shared anonymous session per process, a
/// persisted refresh token (so a restart refreshes instead of signing up),
/// a one-time random startup jitter before any signUp, and an exponential
/// cooldown after failures during which callers fail fast without touching
/// the network.
/// </summary>
internal static class AnonymousAuthCoordinator
{
    internal sealed record Session(string IdToken, string RefreshToken, string UserId, DateTime Expiry);

    internal static readonly SemaphoreSlim Gate = new(1, 1);
    internal static Session? Cached;
    internal static DateTime BlockedUntilUtc = DateTime.MinValue;
    internal static string? LastError;
    internal static int FailureCount;
    internal static bool JitterDone;

    private const string RegKey = @"SOFTWARE\SIONYX";
    private const string TokenValue = "AnonRefreshToken";
    private const string JitterValue = "SignInJitterMaxSeconds";
    private const int DefaultJitterMaxSeconds = 180;

    private static readonly TimeSpan BaseCooldown = TimeSpan.FromSeconds(60);
    private static readonly TimeSpan MaxCooldown = TimeSpan.FromMinutes(10);

    internal static TimeSpan CooldownRemaining
    {
        get
        {
            var left = BlockedUntilUtc - DateTime.UtcNow;
            return left > TimeSpan.Zero ? left : TimeSpan.Zero;
        }
    }

    /// <summary>60s, 2m, 4m, 8m, capped at 10m, plus up to 20% jitter.</summary>
    internal static TimeSpan NextCooldown(int failureCount, Random rng)
    {
        var exp = Math.Min(Math.Max(failureCount, 1) - 1, 10);
        var baseSeconds = Math.Min(BaseCooldown.TotalSeconds * Math.Pow(2, exp), MaxCooldown.TotalSeconds);
        return TimeSpan.FromSeconds(baseSeconds * (1 + rng.NextDouble() * 0.2));
    }

    /// <summary>Random delay in [0, max] seconds; max is registry-overridable (0 disables).</summary>
    internal static TimeSpan PickStartupJitter(Random rng)
    {
        var max = DefaultJitterMaxSeconds;
        try
        {
            using var key = Registry.LocalMachine.OpenSubKey(RegKey);
            if (key?.GetValue(JitterValue) is int v && v >= 0) max = v;
        }
        catch { /* registry unavailable - use default */ }
        return max <= 0 ? TimeSpan.Zero : TimeSpan.FromSeconds(rng.NextDouble() * max);
    }

    internal static void RegisterFailure(string error, Random rng)
    {
        FailureCount++;
        LastError = error;
        BlockedUntilUtc = DateTime.UtcNow + NextCooldown(FailureCount, rng);
    }

    internal static void RegisterSuccess(Session session)
    {
        Cached = session;
        FailureCount = 0;
        BlockedUntilUtc = DateTime.MinValue;
        LastError = null;
        SavePersisted(session.RefreshToken);
    }

    internal static string? LoadPersisted()
    {
        try
        {
            using var key = Registry.CurrentUser.OpenSubKey(RegKey);
            return key?.GetValue(TokenValue) as string;
        }
        catch { return null; }
    }

    internal static void SavePersisted(string refreshToken)
    {
        if (string.IsNullOrEmpty(refreshToken)) return;
        try
        {
            using var key = Registry.CurrentUser.CreateSubKey(RegKey);
            key?.SetValue(TokenValue, refreshToken, RegistryValueKind.String);
        }
        catch (Exception ex)
        {
            Log.ForContext(typeof(AnonymousAuthCoordinator)).Debug(ex, "Could not persist anonymous refresh token");
        }
    }

    internal static void ClearPersisted()
    {
        Cached = null;
        try
        {
            using var key = Registry.CurrentUser.OpenSubKey(RegKey, writable: true);
            key?.DeleteValue(TokenValue, throwOnMissingValue: false);
        }
        catch { /* best effort */ }
    }

    /// <summary>Test helper.</summary>
    internal static void ResetForTests()
    {
        Cached = null;
        BlockedUntilUtc = DateTime.MinValue;
        LastError = null;
        FailureCount = 0;
        JitterDone = false;
    }
}
