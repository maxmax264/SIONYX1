using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.DependencyInjection;
using Serilog; // brings the WriteTo.File(...) extension method into scope
using SionyxInputInjector;

// Must happen before any GetSystemMetrics/SendInput call anywhere in this
// process - see the constant's comment in NativeMethods.cs. Best-effort:
// if this fails (e.g. an OS old enough not to support Per-Monitor V2),
// injection still runs, just potentially with the same DPI-offset bug
// this exists to avoid.
NativeMethods.SetProcessDpiAwarenessContext(NativeMethods.DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2);

// The shared VNC bridge code (VncRelayService & co, linked from SionyxKiosk)
// logs through Serilog's static Log.Logger; without this it would be silent.
// Daily files under C:\ProgramData\SIONYX\logs\host-YYYYMMDD.log.
try
{
    var logDir = @"C:\ProgramData\SIONYX\logs";
    Directory.CreateDirectory(logDir);
    Serilog.Log.Logger = new Serilog.LoggerConfiguration()
        .MinimumLevel.Information()
        .WriteTo.File(
            Path.Combine(logDir, "host-.log"),
            rollingInterval: Serilog.RollingInterval.Day,
            retainedFileCountLimit: 7,
            shared: true)
        .CreateLogger();
}
catch
{
    // logging is best effort - never stop the service from starting
}

var builder = Host.CreateApplicationBuilder(args);

// Registers under the "SionyxInputInjector" Windows Event Log source when
// actually running as a service; falls back to console logging when run
// directly (e.g. `dotnet run` while developing/debugging on a real machine -
// this cannot be tested outside Windows at all, see project README).
builder.Services.AddWindowsService(options =>
{
    options.ServiceName = "SionyxInputInjector";
});

builder.Services.AddSingleton<InputInjector>();
builder.Services.AddSingleton<TightVncInstaller>();
builder.Services.AddHostedService<PipeServerWorker>();
builder.Services.AddHostedService<VncHostWorker>();

var host = builder.Build();
host.Run();
