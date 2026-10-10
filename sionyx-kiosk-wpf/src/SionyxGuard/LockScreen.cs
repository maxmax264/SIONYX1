using System.Drawing;
using System.Windows.Forms;

namespace SionyxGuard;

/// <summary>
/// "--lock" mode: opaque topmost window on every monitor, keyboard swallowed.
/// Fail-safe by design: it exits on its own when the guard stops refreshing lock.flag,
/// so a dead guard can never leave a machine locked forever.
/// </summary>
internal static class LockScreen
{
    private static readonly List<Form> Forms = new();
    private static Native.HookProc? _hookProc; // keep alive - GC'd delegate = crash
    private static IntPtr _hook = IntPtr.Zero;
    private static bool _exiting;
    private const string Message = "המחשב נעול זמנית\nהמערכת מתאוששת, אנא המתן...\n\nSIONYX";

    public static int Run()
    {
        using var mutex = new Mutex(true, @"Local\SionyxGuardLock", out var isNew);
        if (!isNew) return 0;

        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);

        _hookProc = (code, w, l) => code >= 0 ? (IntPtr)1 : Native.CallNextHookEx(_hook, code, w, l);
        _hook = Native.SetWindowsHookEx(Native.WH_KEYBOARD_LL, _hookProc, Native.GetModuleHandle(null), 0);

        Rebuild();
        Cursor.Hide();

        var timer = new System.Windows.Forms.Timer { Interval = 500 };
        timer.Tick += (_, _) =>
        {
            if (!FlagIsFresh()) { Quit(); return; }
            if (Forms.Count != Screen.AllScreens.Length) Rebuild();
            foreach (var f in Forms) { f.TopMost = true; f.BringToFront(); f.Activate(); }
        };
        timer.Start();

        Application.Run();

        if (_hook != IntPtr.Zero) Native.UnhookWindowsHookEx(_hook);
        Cursor.Show();
        return 0;
    }

    private static bool FlagIsFresh()
    {
        try
        {
            var age = DateTime.UtcNow - File.GetLastWriteTimeUtc(GuardPaths.LockFlag);
            return File.Exists(GuardPaths.LockFlag) && age < TimeSpan.FromSeconds(10);
        }
        catch { return false; }
    }

    private static void Quit()
    {
        _exiting = true;
        foreach (var f in Forms.ToArray()) f.Close();
        Application.ExitThread();
    }

    private static void Rebuild()
    {
        foreach (var f in Forms) { f.FormClosing -= OnClosing; f.Close(); }
        Forms.Clear();
        foreach (var screen in Screen.AllScreens)
        {
            var form = new Form
            {
                FormBorderStyle = FormBorderStyle.None,
                StartPosition = FormStartPosition.Manual,
                Bounds = screen.Bounds,
                BackColor = Color.Black,
                ShowInTaskbar = false,
                TopMost = true,
                RightToLeft = RightToLeft.Yes,
                RightToLeftLayout = true,
            };
            form.Controls.Add(new Label
            {
                Text = Message,
                ForeColor = Color.White,
                Font = new Font("Segoe UI", 28f),
                TextAlign = ContentAlignment.MiddleCenter,
                Dock = DockStyle.Fill,
            });
            form.FormClosing += OnClosing;
            form.Show();
            Forms.Add(form);
        }
    }

    private static void OnClosing(object? sender, FormClosingEventArgs e)
    {
        if (!_exiting) e.Cancel = true; // Alt+F4 etc.
    }
}
