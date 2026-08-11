using System.IO;
using System.Text.Json;
using System.Windows;
using Microsoft.Web.WebView2.Core;
using Serilog;
using SionyxKiosk.Infrastructure;
using SionyxKiosk.Services;

namespace SionyxKiosk.Views.Dialogs;

/// <summary>
/// Debug-only dialog for the "תשלום (בדיקה)" screen. Loads the SAME real
/// Nedarim iframe payment.html already uses for regular payment/CreateToken -
/// not a raw server-to-server call - and lets the operator try posting
/// FinishTransaction2 with the user's saved token under several different
/// PaymentType guesses, to see whether Nedarim's iframe itself recognizes a
/// "charge with saved token" flow (which, being iframe-based, wouldn't need
/// PCI-DSS licensing the way a direct API call does - see debugChargeToken /
/// PaymentTestViewModel for the raw-API side of this investigation).
/// </summary>
public partial class PaymentTokenTestDialog : Window
{
    private static readonly ILogger Logger = Log.ForContext<PaymentTokenTestDialog>();

    private readonly OrganizationMetadataService _metadataService;
    private readonly FirebaseClient _firebase;
    private readonly string _userId;
    private LocalFileServer? _server;

    public PaymentTokenTestDialog(
        OrganizationMetadataService metadataService,
        FirebaseClient firebase,
        string userId)
    {
        _metadataService = metadataService;
        _firebase = firebase;
        _userId = userId;

        InitializeComponent();
        Loaded += OnLoaded;
        Closed += OnClosed;
    }

    private void CloseButton_Click(object sender, RoutedEventArgs e) => Close();

    private async void OnLoaded(object sender, RoutedEventArgs e)
    {
        try
        {
            var templatesDir = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Assets", "templates");
            _server = new LocalFileServer(templatesDir, 0);
            _server.Start();

            var webView2DataDir = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "SIONYX", "WebView2");
            var env = await CoreWebView2Environment.CreateAsync(null, webView2DataDir);
            await TestWebView.EnsureCoreWebView2Async(env);

            TestWebView.CoreWebView2.WebMessageReceived += OnWebMessageReceived;

            var url = _server.BaseUrl + "payment-token-test.html";
            Logger.Information("Loading payment token test page: {Url}", url);
            TestWebView.CoreWebView2.Navigate(url);
            TestWebView.CoreWebView2.NavigationCompleted += async (_, args) =>
            {
                if (args.IsSuccess) await InjectConfigAsync();
            };
        }
        catch (Exception ex)
        {
            Logger.Error(ex, "Failed to load payment token test dialog");
            MessageBox.Show("שגיאה בטעינת מסך הבדיקה", "שגיאה", MessageBoxButton.OK, MessageBoxImage.Error);
            Close();
        }
    }

    private async Task InjectConfigAsync()
    {
        var metaResult = await _metadataService.GetOrganizationMetadataAsync(_firebase.OrgId);
        var mosadId = "";
        if (metaResult.IsSuccess && metaResult.Data != null)
        {
            var dataType = metaResult.Data.GetType();
            var val = dataType.GetProperty("nedarim_mosad_id")?.GetValue(metaResult.Data);
            mosadId = val is JsonElement el ? (el.ValueKind == JsonValueKind.String ? el.GetString() ?? "" : el.ToString()) : val?.ToString() ?? "";
        }

        var saveCardApiValid = "";
        var paymentSettingsResult = await _firebase.DbGetAsync("metadata/settings/payment");
        if (paymentSettingsResult.Success && paymentSettingsResult.Data is JsonElement paymentData &&
            paymentData.ValueKind == JsonValueKind.Object &&
            paymentData.TryGetProperty("nedarimApiValid", out var scav))
        {
            saveCardApiValid = scav.GetString() ?? "";
        }

        var kevaId = "";
        var userPhone = "";
        var userFirstName = "";
        var userLastName = "";
        var userResult = await _firebase.DbGetAsync($"users/{_userId}");
        if (userResult.Success && userResult.Data is JsonElement userData)
        {
            if (userData.TryGetProperty("savedCard", out var sc) && sc.TryGetProperty("kevaId", out var kevaEl))
                kevaId = kevaEl.GetString() ?? "";
            if (userData.TryGetProperty("phoneNumber", out var phoneEl)) userPhone = phoneEl.GetString() ?? "";
            if (userData.TryGetProperty("firstName", out var fnEl)) userFirstName = fnEl.GetString() ?? "";
            if (userData.TryGetProperty("lastName", out var lnEl)) userLastName = lnEl.GetString() ?? "";
        }

        var callbackUrl = string.IsNullOrEmpty(_firebase.FunctionsBaseUrl)
            ? $"https://us-central1-{_firebase.ProjectId}.cloudfunctions.net/nedarimCallback"
            : $"{_firebase.FunctionsBaseUrl}/nedarimCallback";

        var config = new
        {
            mosadId, saveCardApiValid, kevaId, amount = "1",
            userPhone, userFirstName, userLastName, callbackUrl,
        };

        Logger.Information("PaymentTokenTestDialog config: mosadId={MosadId} kevaIdSuffix={KevaSuffix}",
            mosadId, kevaId.Length > 4 ? kevaId[^4..] : kevaId);

        var message = JsonSerializer.Serialize(new { action = "setConfig", config });
        TestWebView.CoreWebView2.PostWebMessageAsJson(message);
    }

    private void OnWebMessageReceived(object? sender, CoreWebView2WebMessageReceivedEventArgs e)
    {
        try
        {
            var json = e.WebMessageAsJson;
            using var doc = JsonDocument.Parse(json);
            var root = doc.RootElement;
            if (root.TryGetProperty("action", out var actionEl) && actionEl.GetString() == "debugLog")
            {
                var msg = root.TryGetProperty("message", out var m) ? m.GetString() : "";
                Logger.Information("[payment-token-test.html] {Message}", msg);
            }
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "Failed to parse WebMessage in PaymentTokenTestDialog");
        }
    }

    private void OnClosed(object? sender, EventArgs e)
    {
        try
        {
            TestWebView.Dispose();
            _server?.Stop();
            _server?.Dispose();
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "Error during PaymentTokenTestDialog cleanup");
        }
    }
}
