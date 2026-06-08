code = """using Hardcodet.Wpf.TaskbarNotification;
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
            menu.Items.Add(restoreItem);
            menu.Items.Add(controlItem);
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
            _trayIcon.ForceCreate();
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
"""
open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\TrayIconService.cs', 'w', encoding='utf-8').write(code)
print('OK')
