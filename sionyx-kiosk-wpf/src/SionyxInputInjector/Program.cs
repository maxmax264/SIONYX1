using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.DependencyInjection;
using SionyxInputInjector;

// Must happen before any GetSystemMetrics/SendInput call anywhere in this
// process - see the constant's comment in NativeMethods.cs. Best-effort:
// if this fails (e.g. an OS old enough not to support Per-Monitor V2),
// injection still runs, just potentially with the same DPI-offset bug
// this exists to avoid.
NativeMethods.SetProcessDpiAwarenessContext(NativeMethods.DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2);

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

var host = builder.Build();
host.Run();
