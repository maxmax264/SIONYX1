code = """using Serilog;

namespace SionyxKiosk.Services;

/// <summary>
/// System tray icon - shown only when admin is logged in.
/// </summary>
public class TrayIconService : IDisposable
{
    private System.Windows.Forms.NotifyIcon? _trayIcon;
    private System.Threading.Thread? _thread;

    public event Action? RestoreRequested;
    public event Action? OpenControlPanelRequested;

    public void Show()
    {
        if (_trayIcon != null) return;
        _thread = new System.Threading.Thread(() =>
        {
            var menu = new System.Windows.Forms.ContextMenuStrip();
            menu.Items.Add("החזר את התוכנה", null, (s, e) => RestoreRequested?.Invoke());
            menu.Items.Add("פתח לוח בקרה", null, (s, e) => OpenControlPanelRequested?.Invoke());
            menu.RightToLeft = System.Windows.Forms.RightToLeft.Yes;

            _trayIcon = new System.Windows.Forms.NotifyIcon
            {
                Icon = System.Drawing.SystemIcons.Application,
                Text = "SIONYX",
                ContextMenuStrip = menu,
                Visible = true
            };

            System.Windows.Forms.Application.Run();
        }) { IsBackground = true, Name = "TrayIcon" };
        _thread.SetApartmentState(System.Threading.ApartmentState.STA);
        _thread.Start();
        Log.Information("[Tray] Icon shown");
    }

    public void Hide()
    {
        if (_trayIcon == null) return;
        try
        {
            _trayIcon.Visible = false;
            _trayIcon.Dispose();
            _trayIcon = null;
            System.Windows.Forms.Application.ExitThread();
        }
        catch { }
        Log.Information("[Tray] Icon hidden");
    }

    public void Dispose() => Hide();
}
"""
open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\TrayIconService.cs', 'w', encoding='utf-8').write(code)
print('OK')
