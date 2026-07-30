using System.Globalization;
using System.Runtime.InteropServices;
using System.Windows;
using System.Windows.Data;
using System.Windows.Input;
using System.Windows.Interop;
using System.Windows.Media.Animation;
using Serilog;
using SionyxKiosk.ViewModels;

namespace SionyxKiosk.Views.Windows;

public partial class AuthWindow : Window
{
    private static readonly ILogger Logger = Log.ForContext<AuthWindow>();
    private bool _allowClose;
    private bool _isLoginMode = true;
    private readonly AuthViewModel _vm;

    // Topmost (set in XAML) only controls z-order - it doesn't grant actual
    // OS-level input focus, and plain WPF Activate() can lose to Windows'
    // foreground-lock protection (a background/just-closed process isn't
    // always allowed to steal focus outright). AttachThreadInput is the
    // standard, reliable workaround: briefly share input state with
    // whichever window currently has focus so SetForegroundWindow is
    // actually honored instead of just flashing the taskbar icon.
    [DllImport("user32.dll")]
    private static extern bool SetForegroundWindow(IntPtr hWnd);

    [DllImport("user32.dll")]
    private static extern IntPtr GetForegroundWindow();

    [DllImport("user32.dll")]
    private static extern uint GetWindowThreadProcessId(IntPtr hWnd, IntPtr lpdwProcessId);

    [DllImport("user32.dll")]
    private static extern bool AttachThreadInput(uint idAttach, uint idAttachTo, bool fAttach);

    [DllImport("kernel32.dll")]
    private static extern uint GetCurrentThreadId();

    [DllImport("user32.dll")]
    private static extern bool BringWindowToTop(IntPtr hWnd);

    /// <summary>
    /// Forces this window to actually take OS-level foreground/input focus,
    /// not just visual top-of-z-order (which Topmost already gives it).
    /// Safe to call repeatedly - each call is a brief attach/detach.
    /// </summary>
    public void ForceForeground()
    {
        try
        {
            var hwnd = new WindowInteropHelper(this).EnsureHandle();
            var foreground = GetForegroundWindow();
            if (foreground == hwnd) return;

            var foregroundThreadId = GetWindowThreadProcessId(foreground, IntPtr.Zero);
            var thisThreadId = GetCurrentThreadId();
            var attached = foregroundThreadId != thisThreadId &&
                           AttachThreadInput(thisThreadId, foregroundThreadId, true);
            try
            {
                BringWindowToTop(hwnd);
                SetForegroundWindow(hwnd);
            }
            finally
            {
                if (attached) AttachThreadInput(thisThreadId, foregroundThreadId, false);
            }
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "ForceForeground failed (non-fatal)");
        }
    }

    public AuthWindow(AuthViewModel viewModel)
    {
        _vm = viewModel;
        DataContext = viewModel;
        Resources["StringToVis"] = new Views.Controls.StringToVisibilityConverter();
        Resources["InverseBool"] = new InverseBoolConverter();
        InitializeComponent();

        // WPF PasswordBox doesn't support binding — wire manually.
        LoginPasswordInput.PasswordChanged += (_, _) => viewModel.Password = LoginPasswordInput.Password;
        RegPasswordInput.PasswordChanged += (_, _) => viewModel.Password = RegPasswordInput.Password;

        Logger.Information("AuthWindow constructed. AppVersion={AppVersion}", viewModel.AppVersion);

        // Enter key submits the form. Phone field's Enter moves to the password
        // field instead of submitting - submitting straight from the phone
        // field meant Enter there tried to log in with whatever password was
        // already typed (usually none yet), instead of advancing.
        // PreviewKeyDown (tunneling) instead of KeyDown (bubbling): guarantees
        // this runs before anything else in the tree could react to Enter first.
        LoginPasswordInput.PreviewKeyDown += OnLoginKeyDown;
        LoginPhoneInput.PreviewKeyDown += OnLoginPhoneKeyDown;
        RegPasswordInput.PreviewKeyDown += OnRegisterKeyDown;

        Loaded += (_, _) =>
        {
            // Element.Focus() alone can silently no-op here if the window
            // hasn't actually received OS-level activation yet at the moment
            // Loaded fires. Defer past the current layout/input pass, force
            // real OS foreground first, then set keyboard focus explicitly.
            Dispatcher.BeginInvoke(System.Windows.Threading.DispatcherPriority.Input, new Action(() =>
            {
                ForceForeground();
                LoginPhoneInput.Focus();
                Keyboard.Focus(LoginPhoneInput);
            }));
            _ = viewModel.ReloadBackgroundAsync();
        };

        // Loaded can fire before a just-closed previous window (e.g. after
        // logout: MainWindow.Close() then `new AuthWindow().Show()`) has
        // actually released OS-level focus, so the Loaded-based attempt
        // above can silently lose the race. Activated fires only once
        // Windows has genuinely handed this window the foreground/focus -
        // a much stronger signal - so re-apply there too as a fallback.
        // Guarded so it never yanks focus away from a field the user has
        // already clicked into themselves.
        Activated += (_, _) =>
        {
            if (!LoginPhoneInput.IsKeyboardFocusWithin && !LoginPasswordInput.IsKeyboardFocusWithin)
            {
                LoginPhoneInput.Focus();
                Keyboard.Focus(LoginPhoneInput);
            }
        };
    }

    public void AllowClose() => _allowClose = true;

    // ── Toggle animations ──

    private void ToggleToRegister_Click(object sender, RoutedEventArgs e)
    {
        if (!_isLoginMode) return;
        _isLoginMode = false;
        _vm.IsLoginMode = false;
        _vm.ErrorMessage = "";

        // Sync password to register box
        RegPasswordInput.Password = LoginPasswordInput.Password;

        RegisterPanel.IsHitTestVisible = true;
        LoginPanel.IsHitTestVisible = false;

        var sb = (Storyboard)FindResource("SlideToRegister");
        sb.Begin(this);

        BrandSubtitleBlock.Text = "הצטרף אלינו היום";
        RegPhoneInput.Focus();
    }

    private void ToggleToLogin_Click(object sender, RoutedEventArgs e)
    {
        if (_isLoginMode) return;
        _isLoginMode = true;
        _vm.IsLoginMode = true;
        _vm.ErrorMessage = "";

        // Sync password to login box
        LoginPasswordInput.Password = RegPasswordInput.Password;

        LoginPanel.IsHitTestVisible = true;
        RegisterPanel.IsHitTestVisible = false;

        var sb = (Storyboard)FindResource("SlideToLogin");
        sb.Begin(this);

        BrandSubtitleBlock.Text = "ניהול מחשבים חכם";
        LoginPhoneInput.Focus();
    }

    // ── Enter key to submit ──

    private void OnLoginKeyDown(object sender, System.Windows.Input.KeyEventArgs e)
    {
        if (e.Key != Key.Enter) return;
        Logger.Information("OnLoginKeyDown fired (submit) from sender={Sender}", (sender as FrameworkElement)?.Name);
        if (_vm.LoginCommand.CanExecute(null))
        {
            _vm.LoginCommand.Execute(null);
            e.Handled = true;
        }
    }

    private void OnLoginPhoneKeyDown(object sender, System.Windows.Input.KeyEventArgs e)
    {
        if (e.Key != Key.Enter) return;
        Logger.Information("OnLoginPhoneKeyDown fired (advance to password) from sender={Sender}", (sender as FrameworkElement)?.Name);
        LoginPasswordInput.Focus();
        Keyboard.Focus(LoginPasswordInput);
        e.Handled = true;
    }

    private void OnRegisterKeyDown(object sender, System.Windows.Input.KeyEventArgs e)
    {
        if (e.Key == Key.Enter && _vm.RegisterCommand.CanExecute(null))
        {
            _vm.RegisterCommand.Execute(null);
            e.Handled = true;
        }
    }

    // ── Window chrome ──

    protected override void OnClosing(System.ComponentModel.CancelEventArgs e)
    {
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

public class InverseBoolConverter : IValueConverter
{
    public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
        => value is bool b ? !b : value;
    public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        => value is bool b ? !b : value;
}

public class InverseBoolToVisibilityConverter : IValueConverter
{
    public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
        => value is bool b && b ? Visibility.Collapsed : Visibility.Visible;
    public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        => value is Visibility v && v != Visibility.Visible;
}
