using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.DependencyInjection;
using SionyxInputInjector;

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
builder.Services.AddHostedService<PipeServerWorker>();

var host = builder.Build();
host.Run();
