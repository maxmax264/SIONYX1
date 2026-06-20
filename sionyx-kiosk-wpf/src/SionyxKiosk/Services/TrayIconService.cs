using Hardcodet.Wpf.TaskbarNotification;
using System.Windows;
using System.Windows.Controls;
using Serilog;

namespace SionyxKiosk.Services;

public class TrayIconService : IDisposable
{
    private TaskbarIcon? _trayIcon;
    private MenuItem? _updateItem;

    public event Action? RestoreRequested;
    public event Action? OpenControlPanelRequested;
    public event Action? OpenDashboardRequested;
    public event Action? AboutRequested;
    public event Action? ExitRequested;
    public event Action? CustomizeDesktopRequested;
    public event Action? SaveSnapshotRequested;
    public event Action? SettingsRequested;
    public event Action? StartupSettingsRequested;
    public event Action? CheckUpdateRequested;
    public event Action? ForceUpdateRequested;

    private MenuItem? _customizeItem;

    public void Show(string version = "")
    {
        if (_trayIcon != null) return;
        Application.Current.Dispatcher.Invoke(() =>
        {
            var menu = new ContextMenu();
            if (!string.IsNullOrEmpty(version))
            {
                var versionItem = new MenuItem
                {
                    Header = $"SIONYX v{version}",
                    FlowDirection = FlowDirection.RightToLeft,
                    IsEnabled = false,
                    FontWeight = System.Windows.FontWeights.Bold
                };
                menu.Items.Add(versionItem);
                menu.Items.Add(new Separator());
            }

            var restoreItem = new MenuItem { Header = "החזר את התוכנה", FlowDirection = FlowDirection.RightToLeft };
            restoreItem.Click += (s, e) => RestoreRequested?.Invoke();

            var controlItem = new MenuItem { Header = "פתח לוח בקרה", FlowDirection = FlowDirection.RightToLeft };
            controlItem.Click += (s, e) => OpenControlPanelRequested?.Invoke();

            var dashItem = new MenuItem { Header = "פתח דשבורד", FlowDirection = FlowDirection.RightToLeft };
            dashItem.Click += (s, e) => OpenDashboardRequested?.Invoke();

            var aboutItem = new MenuItem { Header = "אודות", FlowDirection = FlowDirection.RightToLeft };
            aboutItem.Click += (s, e) => AboutRequested?.Invoke();

            _customizeItem = new MenuItem { Header = "עצב שולחן עבודה", FlowDirection = FlowDirection.RightToLeft };
            _customizeItem.Click += (s, e) =>
            {
                if (_customizeItem.Header?.ToString()?.Contains("סיום") == true)
                {
                    _customizeItem.Header = "עצב שולחן עבודה";
                    SaveSnapshotRequested?.Invoke();
                }
                else
                {
                    _customizeItem.Header = "סיום עיצוב";
                    CustomizeDesktopRequested?.Invoke();
                }
            };

            var startupItem = new MenuItem { Header = "הגדרות הפעלה אוטומטית", FlowDirection = FlowDirection.RightToLeft };
            startupItem.Click += (s, e) => StartupSettingsRequested?.Invoke();

            var settingsItem = new MenuItem { Header = "הגדרות", FlowDirection = FlowDirection.RightToLeft };
            settingsItem.Click += (s, e) => SettingsRequested?.Invoke();

            menu.Items.Add(new Separator());

            var checkUpdateItem = new MenuItem { Header = "בדוק עדכון", FlowDirection = FlowDirection.RightToLeft };
            checkUpdateItem.Click += (s, e) => CheckUpdateRequested?.Invoke();

            _updateItem = new MenuItem { Header = "עדכן עכשיו", FlowDirection = FlowDirection.RightToLeft };
            _updateItem.Click += (s, e) => ForceUpdateRequested?.Invoke();

            menu.Items.Add(restoreItem);
            menu.Items.Add(controlItem);
            menu.Items.Add(dashItem);
            menu.Items.Add(aboutItem);
            menu.Items.Add(_customizeItem);
            menu.Items.Add(startupItem);
            menu.Items.Add(settingsItem);
            menu.Items.Add(new Separator());
            menu.Items.Add(checkUpdateItem);
            menu.Items.Add(_updateItem);
            menu.Items.Add(new Separator());

            var exitItem = new MenuItem { Header = "צא מהתוכנה", FlowDirection = FlowDirection.RightToLeft };
            exitItem.Click += (s, e) => ExitRequested?.Invoke();
            menu.Items.Add(exitItem);

            menu.FlowDirection = FlowDirection.RightToLeft;

            var iconPath = System.IO.Path.Combine(AppContext.BaseDirectory, "app-logo.ico");
            System.Drawing.Icon? icon = null;
            if (System.IO.File.Exists(iconPath))
                icon = new System.Drawing.Icon(iconPath);

            _trayIcon = new TaskbarIcon
            {
                ToolTipText = "SIONYX",
                ContextMenu = menu,
                Icon = icon,
            };
        });
        Log.Information("[Tray] Icon shown");
    }

    public void SetUpdateStatus(string status)
    {
        Application.Current.Dispatcher.Invoke(() =>
        {
            if (_updateItem != null)
                _updateItem.Header = status;
        });
    }

    public void ShowBalloon(string title, string message)
    {
        Application.Current.Dispatcher.Invoke(() =>
        {
            _trayIcon?.ShowBalloonTip(title, message, BalloonIcon.Info);
        });
    }

    public void Hide()
    {
        if (_trayIcon == null) return;
        Application.Current.Dispatcher.Invoke(() =>
        {
            _trayIcon.Dispose();
            _trayIcon = null;
        });
        Log.Information("[Tray] Icon hidden");
    }

    public void Dispose() => Hide();
}