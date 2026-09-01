using Serilog;
using SionyxKiosk.Infrastructure;

namespace SionyxKiosk.Services;

public class ComputerHeartbeatService
{
    private static readonly ILogger Logger = Log.ForContext<ComputerHeartbeatService>();
    private const int IntervalSeconds = 60;

    private readonly FirebaseClient _deviceFirebase;
    private readonly string _computerId;
    private System.Timers.Timer? _timer;
    private bool _starting;

    public ComputerHeartbeatService(FirebaseConfig config)
    {
        _deviceFirebase = new FirebaseClient(config);
        _computerId = DeviceInfo.GetDeviceId();
    }

    public void Start()
    {
        if (_timer != null || _starting) return;

        _ = Task.Run(async () =>
        {
            _starting = true;
            try
            {
                var signIn = await _deviceFirebase.SignInAnonymouslyAsync();
                if (!signIn.Success)
                {
                    Logger.Warning("Heartbeat anonymous sign-in failed: {Error}", signIn.Error);
                    return;
                }

                await SendHeartbeatAsync();

                _timer = new System.Timers.Timer(IntervalSeconds * 1000);
                _timer.Elapsed += async (_, _) => await SendHeartbeatAsync();
                _timer.AutoReset = true;
                _timer.Start();
            }
            finally
            {
                _starting = false;
            }
        });
    }

    private async Task SendHeartbeatAsync()
    {
        try
        {
            var result = await _deviceFirebase.DbUpdateAsync($"computers/{_computerId}",
                new Dictionary<string, object>
                {
                    ["heartbeatAt"] = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(),
                });
            if (!result.Success)
                Logger.Warning("Heartbeat write failed: {Error}", result.Error);
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "Heartbeat write threw (non-fatal)");
        }
    }

    public void Stop()
    {
        _timer?.Stop();
        _timer?.Dispose();
        _timer = null;
    }
}