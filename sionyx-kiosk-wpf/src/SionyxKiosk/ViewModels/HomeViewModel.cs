using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using SionyxKiosk.Models;
using System.Windows;
using Serilog;
using SionyxKiosk.Services;

namespace SionyxKiosk.ViewModels;

/// <summary>Home page ViewModel: stats, session controls, messages, operating hours check.</summary>
public partial class HomeViewModel : ObservableObject, IDisposable
{
    private readonly SessionService _session;
    private readonly ChatService _chat;
    private readonly OperatingHoursService _operatingHours;
    private readonly AnnouncementService? _announcements;
    private UserData _user;
    private readonly PrintMonitorService? _printMonitor;
    private bool _disposed;

    [ObservableProperty] private string _remainingTime = "00:00:00";
    [ObservableProperty] private string _printBalance = "0.00 ₪";
    [ObservableProperty] private string _timeExpiry = "—";
    [ObservableProperty] private int _unreadMessages;
    [ObservableProperty] private bool _isSessionActive;
    [ObservableProperty] private bool _isLoading;
    [ObservableProperty] private bool _isEndingSession;
    [ObservableProperty] private string _errorMessage = "";
    [ObservableProperty] private string _welcomeMessage = "";
    [ObservableProperty] private bool _hasNoTime;
    [ObservableProperty] private string _primaryButtonText = "▶  התחל הפעלה";

    public ObservableCollection<Announcement> GlobalAnnouncements { get; } = new();
    public bool HasAnnouncements => GlobalAnnouncements.Count > 0;

    public bool IsSessionInactive => !IsSessionActive;

    /// <summary>Raised when the user wants to view unread messages.</summary>
    public event Action? ViewMessagesRequested;
    public event Action? NewMessageReceived;
    /// <summary>Raised when user clicks "buy package" button.</summary>
    public event Action? NavigateToPackagesRequested;
    /// <summary>Raised after a session is successfully started.</summary>
    public event Action? SessionStartedSuccessfully;
    /// <summary>Raised when user wants to resume an active session.</summary>
    public event Action? ResumeSessionRequested;

    partial void OnIsSessionActiveChanged(bool value)
    {
        OnPropertyChanged(nameof(IsSessionInactive));
    }

    partial void OnIsLoadingChanged(bool value)
    {
        if (!HasNoTime)
            PrimaryButtonText = value ? "מתחיל..." : "▶  התחל הפעלה";
    }

    public HomeViewModel(SessionService session, ChatService chat, OperatingHoursService operatingHours, UserData user, PrintMonitorService? printMonitor = null,
        AnnouncementService? announcements = null)
    {
        _session = session;
        _chat = chat;
        _operatingHours = operatingHours;
        _announcements = announcements;
        _user = user;
        _printMonitor = printMonitor;

        WelcomeMessage = $"שלום, {_user.FullName}!";
        IsSessionActive = _session.IsActive;
        UpdateStats();

        _session.TimeUpdated += OnTimeUpdated;
        _session.SessionStarted += OnSessionStarted;
        _session.SessionEnded += OnSessionEnded;
        if (_printMonitor != null) _printMonitor.JobAllowed += OnPrintJobAllowed;
        if (_printMonitor != null) _printMonitor.BudgetUpdated += OnPrintBudgetUpdated;
        _chat.MessagesReceived += OnMessagesReceived;

        _ = LoadUnreadCountAsync();
        _ = LoadAnnouncementsAsync();
    }

    /// <summary>Called on each new login to refresh user data.</summary>
    public void Reinitialize(UserData user)
    {
        _user = user;
        WelcomeMessage = $"שלום, {_user.FullName}!";
        IsSessionActive = _session.IsActive;
        HasNoTime = _user.RemainingTime <= 0;
        PrimaryButtonText = HasNoTime ? "רכוש חבילה" : "▶  התחל הפעלה";
        ErrorMessage = "";
        UpdateStats();
        _ = LoadUnreadCountAsync();
        _ = LoadAnnouncementsAsync();
    }

    private async Task LoadUnreadCountAsync()
    {
        var result = await _chat.GetUnreadMessagesAsync();
        if (result.IsSuccess && result.Data is List<Dictionary<string, object?>> msgs)
            UnreadMessages = msgs.Count;
    }

    [RelayCommand]
    private async Task StartSessionAsync()
    {
        if (_session.IsActive) return;
        IsLoading = true;
        ErrorMessage = "";

        try
        {
            // Check operating hours before starting
            var (isAllowed, reason) = _operatingHours.IsWithinOperatingHours();
            if (!isAllowed)
            {
                ErrorMessage = reason ?? "לא ניתן להתחיל הפעלה מחוץ לשעות הפעילות";
                return;
            }

            if (_user.RemainingTime <= 0)
            {
                ErrorMessage = "אין לך זמן שימוש זמין. אנא רכוש חבילה.";
                return;
            }

            var result = await _session.StartSessionAsync(_user.RemainingTime);

            if (result.IsSuccess)
            {
                IsSessionActive = true;
                Log.Information("[SESSION] Session STARTED successfully for user={User} remainingTime={Time}",
                    _user.FullName, _user.RemainingTime);
                SessionStartedSuccessfully?.Invoke();
            }
            else
            {
                Log.Warning("[SESSION] Session START failed: {Error}", result.Error);
                ErrorMessage = result.Error ?? "שגיאה";
            }
        }
        catch (Exception ex)
        {
            Serilog.Log.Error(ex, "StartSession failed");
            ErrorMessage = "שגיאה בהתחלת הפעלה. נסה שוב.";
        }
        finally
        {
            IsLoading = false;
        }
    }

    [RelayCommand]
    private async Task EndSessionAsync()
    {
        if (!_session.IsActive || IsEndingSession) return;
        IsEndingSession = true;
        ErrorMessage = "";

        try
        {
            Log.Information("[SESSION] Ending session for user={User}", _user.FullName);
            await _session.EndSessionAsync("user");
            IsSessionActive = false;

            _user.RemainingTime = Math.Max(0, _session.RemainingTime);
            Log.Information("[SESSION] Session ENDED - remainingTime={Time} printBalance={Balance}",
                _user.RemainingTime, _user.PrintBalance);
            UpdateStats();
        }
        catch (Exception ex)
        {
            Serilog.Log.Error(ex, "EndSession failed");
            ErrorMessage = "שגיאה בסיום הפעלה. נסה שוב.";
        }
        finally
        {
            IsEndingSession = false;
        }
    }

    [RelayCommand]
    private void ViewMessages()
    {
        if (UnreadMessages > 0)
            ViewMessagesRequested?.Invoke();
    }

    [RelayCommand]
    private void BuyPackage()
    {
        NavigateToPackagesRequested?.Invoke();
    }

    [RelayCommand]
    private void ResumeSession()
    {
        ResumeSessionRequested?.Invoke();
    }

    // ── Event handlers ──────────────────────────────────────────

    private void OnTimeUpdated(int remaining)
    {
        Application.Current?.Dispatcher.BeginInvoke(() =>
        {
            var ts = TimeSpan.FromSeconds(Math.Max(0, remaining));
            RemainingTime = ts.ToString(@"hh\:mm\:ss");
        });
    }

    private void OnSessionStarted()
    {
        IsSessionActive = true;
    }

    private void OnSessionEnded(string reason)
    {
        IsSessionActive = false;
        _user.RemainingTime = Math.Max(0, _session.RemainingTime);
        UpdateStats();
    }

    private void OnMessagesReceived(List<Dictionary<string, object?>> msgs)
    {
        var count = msgs.Count;
        Application.Current?.Dispatcher.BeginInvoke(() =>
        {
            var isNew = UnreadMessages == 0 && count > 0;
            UnreadMessages = count;
            if (isNew)
                NewMessageReceived?.Invoke();
        });
    }

    // ── Helpers ─────────────────────────────────────────────────

    private void UpdateStats()
    {
        HasNoTime = _user.RemainingTime <= 0;

        if (_user.RemainingTime > 0)
        {
            var ts = TimeSpan.FromSeconds(_user.RemainingTime);
            RemainingTime = ts.ToString(@"hh\:mm\:ss");
        }
        else
        {
            RemainingTime = "—";
        }

        PrintBalance = _user.PrintBalance > 0 ? $"{_user.PrintBalance:F2} ₪" : "—";
        PrimaryButtonText = HasNoTime ? "קנה חבילה" : "▶  התחל הפעלה";
        TimeExpiry = FormatExpiry(_user.TimeExpiresAt, _user.RemainingTime);
    }

    private async Task LoadAnnouncementsAsync()
    {
        if (_announcements == null) return;
        try
        {
            var result = await _announcements.GetActiveAnnouncementsAsync();
            if (result.IsSuccess && result.Data is List<Announcement> list)
            {
                GlobalAnnouncements.Clear();
                foreach (var a in list)
                    GlobalAnnouncements.Add(a);
                OnPropertyChanged(nameof(HasAnnouncements));
            }
        }
        catch (Exception ex)
        {
            Serilog.Log.Error(ex, "Failed to load announcements");
        }
    }

    internal static string FormatExpiry(string? expiresAt, int remainingTime = -1)
    {
        if (string.IsNullOrEmpty(expiresAt) || !DateTime.TryParse(expiresAt, out var dt))
            return remainingTime > 0 ? "ללא הגבלה" : "אין";

        if (dt <= DateTime.Now)
            return "פג תוקף";

        return dt.ToString("dd/MM/yyyy HH:mm");
    }

    // ── Cleanup ─────────────────────────────────────────────────

    public void Dispose()
    {
        if (_disposed) return;
        _disposed = true;
        Log.Warning("[HVM] HomeViewModel.Dispose() called — caller: {Caller}",
            new System.Diagnostics.StackTrace(1, false).ToString().Split('\n')[0].Trim());

        _session.TimeUpdated -= OnTimeUpdated;
        _session.SessionStarted -= OnSessionStarted;
        _session.SessionEnded -= OnSessionEnded;
        _chat.MessagesReceived -= OnMessagesReceived;
        if (_printMonitor != null) _printMonitor.JobAllowed -= OnPrintJobAllowed;
        if (_printMonitor != null) _printMonitor.BudgetUpdated -= OnPrintBudgetUpdated;

        GC.SuppressFinalize(this);
    }
    private void OnPrintJobAllowed(string doc, int pages, double cost, double remaining)
    {
        Log.Debug("[HVM] OnPrintJobAllowed doc={Doc} pages={Pages} cost={Cost} remaining={Remaining}",
            doc, pages, cost, remaining);
        _user.PrintBalance = remaining;
        Application.Current?.Dispatcher.InvokeAsync(() => PrintBalance = remaining > 0 ? $"{remaining:F2} ₪" : "—");
    }
    private void OnPrintBudgetUpdated(double balance)
    {
        Log.Debug("[HVM] OnPrintBudgetUpdated balance={Balance}", balance);
        _user.PrintBalance = balance;
        Application.Current?.Dispatcher.InvokeAsync(() => PrintBalance = balance > 0 ? $"{balance:F2} ₪" : "—");
    }
}



