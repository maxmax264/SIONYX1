using Hardcodet.Wpf.TaskbarNotification;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media.Imaging;
using Serilog;

namespace SionyxKiosk.Services;

/// <summary>
/// System tray icon - shown only when admin is logged in.
/// </summary>
public class TrayIconService : IDisposable
{
    private TaskbarIcon? _trayIcon;

    public event Action? RestoreRequested;
    public event Action? OpenControlPanelRequested;
    public event Action? OpenDashboardRequested;
    public event Action? AboutRequested;
    public event Action? ExitRequested;
    public event Action? CustomizeDesktopRequested;
    public event Action? SaveSnapshotRequested;
    public event Action? SettingsRequested;
    public event Action? StartupSettingsRequested;

    private MenuItem? _customizeItem;

    public void Show()
    {
        if (_trayIcon != null) return;
        Application.Current.Dispatcher.Invoke(() =>
        {
            var menu = new ContextMenu();
            var restoreItem = new MenuItem { Header = "החזר את התוכנה", FlowDirection = FlowDirection.RightToLeft };
            restoreItem.Click += (s, e) => RestoreRequested?.Invoke();
            var controlItem = new MenuItem { Header = "פתח לוח בקרה", FlowDirection = FlowDirection.RightToLeft };
            controlItem.Click += (s, e) => OpenControlPanelRequested?.Invoke();
            var separator = new Separator();
            var exitItem = new MenuItem { Header = "צא מהתוכנה", FlowDirection = FlowDirection.RightToLeft };
            exitItem.Click += (s, e) => ExitRequested?.Invoke();
            var dashItem = new MenuItem { Header = "פתח דשבורד", FlowDirection = FlowDirection.RightToLeft };
            dashItem.Click += (s, e) => OpenDashboardRequested?.Invoke();
            var aboutItem = new MenuItem { Header = "אודות", FlowDirection = FlowDirection.RightToLeft };
            aboutItem.Click += (s, e) => AboutRequested?.Invoke();
            menu.Items.Add(restoreItem);
            menu.Items.Add(controlItem);
            menu.Items.Add(dashItem);
            menu.Items.Add(aboutItem);
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
            menu.Items.Add(_customizeItem);
            var startupItem = new MenuItem { Header = "הגדרות הפעלה אוטומטית", FlowDirection = FlowDirection.RightToLeft };
            startupItem.Click += (s, e) => StartupSettingsRequested?.Invoke();
            menu.Items.Add(startupItem);
            var settingsItem = new MenuItem { Header = "הגדרות", FlowDirection = FlowDirection.RightToLeft };
            settingsItem.Click += (s, e) => SettingsRequested?.Invoke();
            menu.Items.Add(settingsItem);
            menu.Items.Add(new Separator());
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
