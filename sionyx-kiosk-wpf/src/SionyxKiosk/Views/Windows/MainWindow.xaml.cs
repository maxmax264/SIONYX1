using System.Globalization;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Controls.Primitives;
using System.Windows.Data;
using System.Windows.Input;
using SionyxKiosk.ViewModels;
using SionyxKiosk.Views.Pages;
using Serilog;

namespace SionyxKiosk.Views.Windows;

public partial class MainWindow : Window
{
    private readonly MainViewModel _vm;
    private readonly IServiceProvider _services;
    private bool _initialized;
    private bool _allowClose;
    private Page? _currentPage;
    private SionyxKiosk.Services.TrayIconService? _trayIcon;

    public MainWindow(MainViewModel viewModel, IServiceProvider services)
    {
        _vm = viewModel;
        _services = services;
        DataContext = viewModel;
        Resources["InverseBool"] = new InverseBoolConverter();
        InitializeComponent();
        _initialized = true;

        Loaded += (_, _) =>
        {
            Dispatcher.InvokeAsync(() => NavigateToPage("Home"), System.Windows.Threading.DispatcherPriority.Loaded);
            UpdateAvatarInitials();
            if (viewModel.CurrentUser?.IsAdmin == true)
            {
                _trayIcon = new SionyxKiosk.Services.TrayIconService();
                _trayIcon.RestoreRequested += () => Dispatcher.Invoke(() => { WindowState = System.Windows.WindowState.Maximized; Topmost = true; Activate(); });
                _trayIcon.OpenControlPanelRequested += () => Services.KioskPolicyService.RunWithControlPanel(() => System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo("control.exe") { UseShellExecute = true }));
                _trayIcon.Show();
            }
        };

        viewModel.PropertyChanged += (_, e) =>
        {
            if (e.PropertyName == nameof(MainViewModel.CurrentUser))
                UpdateAvatarInitials();
        };
    }

    private void UpdateAvatarInitials()
    {
        var name = _vm.CurrentUser?.FullName;
        if (string.IsNullOrWhiteSpace(name))
        {
            AvatarInitials.Text = "?";
            return;
        }
        var parts = name.Trim().Split(' ', StringSplitOptions.RemoveEmptyEntries);
        AvatarInitials.Text = parts.Length >= 2
            ? $"{parts[0][0]}{parts[^1][0]}"
            : $"{parts[0][0]}";
    }

    /// <summary>Allow the window to close (called from admin exit or proper logout).</summary>
    public void AllowClose() => _allowClose = true;

    private void NavButton_Checked(object sender, RoutedEventArgs e)
    {
        if (!_initialized) return;
        if (sender is RadioButton rb && rb.Tag is string page)
        {
            _vm.CurrentPage = page;
            NavigateToPage(page);
        }
    }

    private void NavigateToPage(string page)
    {
        if (ContentFrame == null) return;

        try
        {
            // Dispose previous page's ViewModel if it implements IDisposable,
            // BUT skip HomeViewModel — it is a singleton and must stay alive.
            if (_currentPage?.DataContext is IDisposable disposableVm
                && _currentPage.DataContext is not HomeViewModel)
            {
                Log.Debug("[NAV] Disposing ViewModel {Type}", disposableVm.GetType().Name);
                disposableVm.Dispose();
            }

            Log.Information("[NAV] NavigateTo={Page} prev={Prev}", page,
                _currentPage?.GetType().Name ?? "none");

            var pageInstance = page switch
            {
                "Home" => _services.GetService(typeof(HomePage)),
                "Packages" => _services.GetService(typeof(PackagesPage)),
                "History" => _services.GetService(typeof(HistoryPage)),
                "PrintHistory" => _services.GetService(typeof(PrintHistoryPage)),
                "Profile" => _services.GetService(typeof(ProfilePage)),
                "Help" => _services.GetService(typeof(HelpPage)),
                "Messages" => _services.GetService(typeof(MessagesPage)),
                _ => _services.GetService(typeof(HomePage))
            };

            if (pageInstance is Page p)
            {
                _currentPage = p;
                Log.Debug("[NAV] Navigated to {Page} VM={VM}", page,
                    p.DataContext?.GetType().Name ?? "null");
                // Set Content directly instead of Navigate() to avoid
                // WPF Frame journal accumulation (keeps all old pages in memory).
                ContentFrame.Content = p;
            }
        }
        catch (Exception ex)
        {
            Serilog.Log.Error(ex, "Failed to navigate to page {Page}", page);
        }
    }

    /// <summary>Navigate back to Home page (called after session ends to refresh the view).</summary>
    public void NavigateHome()
    {
        NavHome.IsChecked = true;
        _vm.CurrentPage = "Home";
        NavigateToPage("Home");
    }

    /// <summary>Navigate to the Packages page (called when user needs to buy a package).</summary>
    public void NavigateToPackages()
    {
        NavPackages.IsChecked = true;
        _vm.CurrentPage = "Packages";
        NavigateToPage("Packages");
    }

    /// <summary>Show a toast notification in the content area.</summary>
    public void ShowToast(string title, string message,
        Controls.ToastNotification.ToastType type = Controls.ToastNotification.ToastType.Info,
        int durationMs = 3000)
    {
        Toast.Show(title, message, type, durationMs);
    }

    protected override void OnClosing(System.ComponentModel.CancelEventArgs e)
    {
        // Dispose current page ViewModel on window close
        if (_currentPage?.DataContext is IDisposable disposable)
            disposable.Dispose();

        _trayIcon?.Hide();
        _trayIcon?.Dispose();
        _trayIcon = null;
        if (!_allowClose)
        {
            e.Cancel = true;
            return;
        }
        base.OnClosing(e);
    }

    protected override void OnKeyDown(System.Windows.Input.KeyEventArgs e)
    {
        if (e.Key == Key.Escape || e.Key == Key.System)
        {
            e.Handled = true;
            return;
        }
        base.OnKeyDown(e);
    }
}
