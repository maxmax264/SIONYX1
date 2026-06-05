using System.Windows;
using Serilog;
using SionyxKiosk.Infrastructure;

namespace SionyxKiosk.Views.Windows;

public partial class VerificationWaitingWindow : Window
{
    private readonly FirebaseClient _firebase;
    private readonly string _userId;
    private CancellationTokenSource? _cts;
    private bool _allowClose;

    public event Action? VerificationCompleted;
    public event Action? BackToLogin;

    public VerificationWaitingWindow(FirebaseClient firebase, string userId, string phoneNumber)
    {
        _firebase = firebase;
        _userId = userId;
        InitializeComponent();
        PhoneNumberText.Text = phoneNumber;
        LogoutButton.Click += (_, _) => { BackToLogin?.Invoke(); };
        Loaded += (_, _) => StartListening();
    }

    public void AllowClose() => _allowClose = true;

    private void StartListening()
    {
        _cts = new CancellationTokenSource();
        var token = _cts.Token;

        Task.Run(async () =>
        {
            Log.Information("VerificationWaiting: polling phoneVerified for {UserId}", _userId);
            while (!token.IsCancellationRequested)
            {
                try
                {
                    var result = await _firebase.DbGetAsync($"users/{_userId}");
                    if (result.Success &&
                        result.Data is System.Text.Json.JsonElement data &&
                        data.TryGetProperty("phoneVerified", out var pv) &&
                        pv.GetBoolean())
                    {
                        Log.Information("VerificationWaiting: phoneVerified=true, proceeding");
                        Dispatcher.Invoke(() => VerificationCompleted?.Invoke());
                        return;
                    }
                }
                catch (Exception ex)
                {
                    Log.Warning(ex, "VerificationWaiting: poll error");
                }
                await Task.Delay(3000, token);
            }
        }, token);
    }

    protected override void OnClosing(System.ComponentModel.CancelEventArgs e)
    {
        if (!_allowClose) { e.Cancel = true; return; }
        _cts?.Cancel();
        base.OnClosing(e);
    }
}
