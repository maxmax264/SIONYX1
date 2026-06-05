path = r'.\src\SionyxKiosk\Services\ForceLogoutService.cs'
new_content = """using System.Text.Json;
using Serilog;
using SionyxKiosk.Infrastructure;
namespace SionyxKiosk.Services;
public class ForceLogoutService
{
    private static readonly ILogger Log = Serilog.Log.ForContext<ForceLogoutService>();
    private readonly FirebaseClient _firebase;
    private SseListener? _listener;
    private string? _userId;
    private bool _isFirstEvent;
    private volatile bool _isPaused;
    public bool IsPaused => _isPaused;
    private DateTime _pausedAt = DateTime.MinValue;
    private int _listenerVersion = 0;
    public event Action<string>? ForceLogout;
    public ForceLogoutService(FirebaseClient firebase)
    {
        _firebase = firebase;
    }
    public void StartListening(string userId)
    {
        _userId = userId;
        StopListening();
        var version = System.Threading.Interlocked.Increment(ref _listenerVersion);
        _ = ClearStaleDataAndListenAsync(userId, version);
    }
    private async Task ClearStaleDataAndListenAsync(string userId, int version)
    {
        if (version != _listenerVersion) return;
        try
        {
            await _firebase.DbDeleteAsync($"users/{userId}/forceLogout");
            Log.Debug("ForceLogoutService: cleared stale force-logout data");
        }
        catch (Exception ex)
        {
            Log.Debug(ex, "ForceLogoutService: could not clear stale data (non-fatal)");
        }
        if (version != _listenerVersion) return;
        _isFirstEvent = true;
        var path = $"users/{userId}/forceLogout";
        _listener = _firebase.DbListen(path, OnEvent);
        Log.Information("ForceLogoutService: listening on {Path}", path);
    }
    public void Pause() { _isPaused = true; _pausedAt = DateTime.UtcNow; }
    public void Resume() { _isPaused = false; }
    public void StopListening()
    {
        _listener?.Stop();
        _listener = null;
    }
    private void OnEvent(string eventType, JsonElement? data)
    {
        if (eventType != "put" || data == null) return;
        if (_isPaused || (DateTime.UtcNow - _pausedAt).TotalSeconds < 10) return;
        try
        {
            if (_isFirstEvent)
            {
                _isFirstEvent = false;
                if (data.Value.ValueKind != JsonValueKind.Null)
                {
                    Log.Debug("ForceLogoutService: ignoring initial SSE state (stale data)");
                    _ = _firebase.DbDeleteAsync($"users/{_userId}/forceLogout");
                }
                return;
            }
            if (data.Value.ValueKind == JsonValueKind.Null) return;
            var reason = "admin_forced";
            if (data.Value.TryGetProperty("reason", out var r))
                reason = r.GetString() ?? reason;
            Log.Warning("ForceLogoutService: received force-logout, reason={Reason}", reason);
            ForceLogout?.Invoke(reason);
            _ = _firebase.DbDeleteAsync($"users/{_userId}/forceLogout");
        }
        catch (Exception ex)
        {
            Log.Error(ex, "ForceLogoutService: error processing event");
        }
    }
}
"""
open(path, 'w', encoding='utf-8').write(new_content)
print('OK')
