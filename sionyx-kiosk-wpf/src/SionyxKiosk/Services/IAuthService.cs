using SionyxKiosk.Models;

namespace SionyxKiosk.Services;

public interface IAuthService
{
    UserData? CurrentUser { get; }

    /// <summary>Raised when the session dies from underneath the app (not an explicit user logout).</summary>
    event Action? SessionExpired;

    Task<bool> IsLoggedInAsync();
    Task<ServiceResult> LoginAsync(string phone, string password);
    Task<ServiceResult> RegisterAsync(string phone, string password, string firstName, string lastName, string email = "");
    Task LogoutAsync();
    Task<ServiceResult> UpdateUserDataAsync(Dictionary<string, object> updates);
    Task<ServiceResult> RefreshCurrentUserAsync();
}
