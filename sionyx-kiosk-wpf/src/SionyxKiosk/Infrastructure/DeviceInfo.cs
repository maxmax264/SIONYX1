using System.IO;
using System.Net.NetworkInformation;
using System.Security.Cryptography;
using System.Text;
using Serilog;

namespace SionyxKiosk.Infrastructure;

/// <summary>
/// Device identification utilities for PC registration and tracking.
/// </summary>
public static class DeviceInfo
{
    private static readonly ILogger Logger = Log.ForContext(typeof(DeviceInfo));

    private static readonly Lazy<string> _deviceIdLazy = new(ComputeDeviceId);

    /// <summary>
    /// Generate a unique device ID based on hardware characteristics.
    /// Uses MAC address for stability, falls back to hash of computer name.
    /// Computed once and cached: NetworkInterface.GetAllNetworkInterfaces()
    /// enumeration order isn't guaranteed stable across calls on machines
    /// with more than one active non-loopback adapter (Wi-Fi + VPN/Bluetooth/
    /// virtual switch, etc), which previously made two calls in the same
    /// process intermittently return different values.
    /// </summary>
    public static string GetDeviceId() => _deviceIdLazy.Value;

    private static string ComputeDeviceId()
    {
        try
        {
            var mac = GetMacAddress();
            if (mac != null)
                return mac.Replace(":", "").ToLowerInvariant();

            // Fallback (no MAC yet): network-independent hash id
            return GetFallbackDeviceId();
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "Failed to generate device ID");
            return Guid.NewGuid().ToString("N")[..16];
        }
    }

    /// <summary>
    /// Network-independent id (hash of machine name + OS). GetDeviceId() returns this
    /// when no MAC is available yet, so a machine can be registered under it;
    /// exposed so the SYSTEM host service can also listen under it.
    /// </summary>
    public static string GetFallbackDeviceId()
    {
        var computerName = GetComputerName();
        var platformInfo = $"{Environment.OSVersion.Platform}-{Environment.Is64BitOperatingSystem}";
        var combined = $"{computerName}-{platformInfo}";
        var hash = SHA256.HashData(Encoding.UTF8.GetBytes(combined));
        return Convert.ToHexString(hash)[..16].ToLowerInvariant();
    }

    /// <summary>
    /// Get the installed app version - Registry first (production, set by the MSI
    /// installer/auto-updater), falling back to version.json next to the exe (dev).
    /// Shared by the login screen watermark and the heartbeat write, so both agree.
    /// </summary>
    public static string GetAppVersion()
    {
        try
        {
            var reg = RegistryConfig.ReadValue("Version");
            if (!string.IsNullOrWhiteSpace(reg)) return reg;
        }
        catch { }

        try
        {
            var p = Path.Combine(AppContext.BaseDirectory, "version.json");
            if (File.Exists(p))
            {
                var json = File.ReadAllText(p);
                using var doc = System.Text.Json.JsonDocument.Parse(json);
                if (doc.RootElement.TryGetProperty("version", out var v)) return v.GetString() ?? "1.0.0";
            }
        }
        catch { }

        return "1.0.0";
    }

    /// <summary>Get the computer name/hostname.</summary>
    public static string GetComputerName()
    {
        try
        {
            return Environment.MachineName;
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "Failed to get computer name");
            return "Unknown-PC";
        }
    }

    /// <summary>
    /// Get computer information for Firebase registration.
    /// </summary>
    public static Dictionary<string, object> GetComputerInfo()
    {
        try
        {
            return new Dictionary<string, object>
            {
                ["computerName"] = GetComputerName(),
                ["deviceId"] = GetDeviceId(),
            };
        }
        catch (Exception ex)
        {
            Logger.Error(ex, "Failed to get computer info");
            return new Dictionary<string, object>
            {
                ["computerName"] = "Unknown-PC",
                ["deviceId"] = Guid.NewGuid().ToString("N")[..16],
            };
        }
    }

    /// <summary>Get MAC address of the primary network interface.</summary>
    private static string? GetMacAddress()
    {
        try
        {
            var nic = NetworkInterface
                .GetAllNetworkInterfaces()
                .FirstOrDefault(n =>
                    n.OperationalStatus == OperationalStatus.Up &&
                    n.NetworkInterfaceType != NetworkInterfaceType.Loopback);

            if (nic == null) return null;

            var bytes = nic.GetPhysicalAddress().GetAddressBytes();
            if (bytes.Length == 0) return null;

            return string.Join(":", bytes.Select(b => b.ToString("x2")));
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "Failed to get MAC address");
            return null;
        }
    }
}
