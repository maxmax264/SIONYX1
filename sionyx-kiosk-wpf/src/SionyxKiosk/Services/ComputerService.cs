using SionyxKiosk.Infrastructure;

namespace SionyxKiosk.Services;

/// <summary>
/// Manages computer/PC registration and tracking in Firebase.
/// </summary>
public class ComputerService : BaseService
{
    protected override string ServiceName => "ComputerService";

    public ComputerService(FirebaseClient firebase) : base(firebase) { }

    public string GetComputerId() => DeviceInfo.GetDeviceId();

    public async Task<ServiceResult> RegisterComputerAsync(string? computerName = null, string? location = null)
    {
        try
        {
            LogOperation("RegisterComputer");
            var info = DeviceInfo.GetComputerInfo();
            var computerId = info["deviceId"].ToString()!;

            // Priority: 1) passed param, 2) registry custom name, 3) Windows hostname, 4) fallback
            var name = info["computerName"].ToString()!;
            if (!string.IsNullOrEmpty(computerName))
                name = computerName;
            else
            {
                var registryName = Infrastructure.RegistryConfig.ReadValue("ComputerName");
                if (!string.IsNullOrEmpty(registryName))
                    name = registryName;
                else if (name == "Unknown-PC")
                    name = $"PC-{computerId[..8].ToUpper()}";
            }

            // The dashboard owns the name once one exists there: renaming a
            // computer in the dashboard (e.g. after machines are physically
            // moved) must stick, and used to be silently reverted to the
            // install-time registry value on the next login. We only write the
            // name here when Firebase has none yet.
            var existing = await Firebase.DbGetAsync($"computers/{computerId}/computerName");
            var hasExistingName = existing.Success
                && existing.Data is System.Text.Json.JsonElement nameEl
                && nameEl.ValueKind == System.Text.Json.JsonValueKind.String
                && !string.IsNullOrWhiteSpace(nameEl.GetString());

            var now = DateTime.Now.ToString("o");
            var data = new Dictionary<string, object?>
            {
                ["currentUserId"] = null,
                ["isActive"] = false,
                ["lastSeen"] = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(),
                ["createdAt"] = now,
                ["updatedAt"] = now,
            };
            if (!hasExistingName)
                data["computerName"] = name;
            if (!string.IsNullOrEmpty(location))
                data["location"] = location;

            var result = await Firebase.DbUpdateAsync($"computers/{computerId}", data);
            if (!result.Success)
                return Error("Failed to register computer");

            Logger.Information("Computer registered: {Id}", computerId);
            return Success(new { computerId, computerName = info["computerName"].ToString() });
        }
        catch (Exception ex)
        {
            return Error(HandleFirebaseError(ex, "RegisterComputer"));
        }
    }

    public async Task<ServiceResult> AssociateUserWithComputerAsync(string userId, string computerId, bool isLogin = false)
    {
        try
        {
            var now = DateTime.Now.ToString("o");
            var ts = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
            var userUpdates = new Dictionary<string, object?> { ["currentComputerId"] = computerId, ["updatedAt"] = now };
            if (isLogin) userUpdates["isLoggedIn"] = true;

            var result = await Firebase.DbUpdateAsync($"users/{userId}", userUpdates);
            if (result.Success)
            {
                await Firebase.DbUpdateAsync($"computers/{computerId}",
                    new Dictionary<string, object>
                    {
                        ["currentUserId"] = userId,
                        ["isActive"] = true,
                        ["lastSeen"] = ts,
                        ["lastUserLogin"] = now,
                        ["updatedAt"] = now,
                    });
            }
            return result.Success ? Success() : Error(result.Error ?? "Failed");
        }
        catch (Exception ex)
        {
            return Error(HandleFirebaseError(ex, "AssociateUser"));
        }
    }

    public async Task<ServiceResult> DisassociateUserFromComputerAsync(string userId, string computerId, bool isLogout = false)
    {
        try
        {
            var now = DateTime.Now.ToString("o");
            var ts = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
            var userUpdates = new Dictionary<string, object?> { ["currentComputerId"] = (object?)null, ["updatedAt"] = now };
            if (isLogout) userUpdates["isLoggedIn"] = false;

            await Firebase.DbUpdateAsync($"users/{userId}", userUpdates);
            await Firebase.DbUpdateAsync($"computers/{computerId}",
                new Dictionary<string, object?>
                {
                    ["currentUserId"] = null,
                    ["isActive"] = false,
                    ["lastSeen"] = ts,
                    ["updatedAt"] = now,
                });

            return Success();
        }
        catch (Exception ex)
        {
            return Error(HandleFirebaseError(ex, "DisassociateUser"));
        }
    }
}
