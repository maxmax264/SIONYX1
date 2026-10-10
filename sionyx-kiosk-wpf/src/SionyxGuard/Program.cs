using Serilog;
using SionyxGuard;

// "--lock": same exe, run inside the user's session by the service, draws the lock screen.
if (args.Contains("--lock"))
    return LockScreen.Run();

try
{
    var logDir = @"C:\ProgramData\SIONYX\logs";
    Directory.CreateDirectory(logDir);
    Log.Logger = new LoggerConfiguration()
        .MinimumLevel.Information()
        .WriteTo.File(Path.Combine(logDir, "guard-.log"), rollingInterval: RollingInterval.Day, retainedFileCountLimit: 14, shared: true)
        .CreateLogger();
}
catch { /* logging is best effort - never stop the guard from starting */ }

var builder = Host.CreateApplicationBuilder(args);
builder.Services.AddWindowsService(o => o.ServiceName = "SionyxGuard");
builder.Services.AddHostedService<GuardWorker>();
builder.Build().Run();
return 0;
