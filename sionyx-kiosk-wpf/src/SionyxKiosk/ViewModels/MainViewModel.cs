using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using SionyxKiosk.Models;
using SionyxKiosk.Services;

namespace SionyxKiosk.ViewModels;

/// <summary>Main window ViewModel: navigation, user info, session state.</summary>
public partial class MainViewModel : ObservableObject
{
    private readonly AuthService _auth;

    [ObservableProperty] private string _currentPage = "Home";
    [ObservableProperty] private UserData? _currentUser;
    [ObservableProperty] private bool _isSidebarCollapsed;
    [ObservableProperty] private bool _isLoggingOut;

    /// <summary>Raised when the user requests logout. App.xaml.cs handles the actual logout.</summary>
    public event Action? LogoutRequested;

    public MainViewModel(AuthService auth)
    {
        _auth = auth;
        CurrentUser = auth.CurrentUser;
        _auth.SessionExpired += OnSessionExpired;
    }

    // Session died server-side (refresh token revoked/expired) rather than
    // an explicit user logout - route through the same LogoutRequested flow
    // App.xaml.cs already handles, so the kiosk lands back on the login
    // screen instead of sitting there with every background SSE listener
    // silently failing forever. Fires from a background SSE task, not the
    // UI thread, so marshal before touching the observable property.
    private void OnSessionExpired()
    {
        System.Windows.Application.Current?.Dispatcher.InvokeAsync(() =>
        {
            if (IsLoggingOut) return;
            IsLoggingOut = true;
            LogoutRequested?.Invoke();
        });
    }

    [RelayCommand]
    private void Navigate(string page)
    {
        CurrentPage = page;
    }

    [RelayCommand]
    private void Logout()
    {
        if (IsLoggingOut) return;
        IsLoggingOut = true;

        // Don't call auth.LogoutAsync() here ג€” the App.xaml.cs OnLogoutRequested
        // handler owns the full logout sequence (stop services ג†’ logout ג†’ show auth window).
        // Calling it here would double-logout and could race with service teardown.
        LogoutRequested?.Invoke();
    }

    [RelayCommand]
    private void ToggleSidebar()
    {
        IsSidebarCollapsed = !IsSidebarCollapsed;
    }
}
