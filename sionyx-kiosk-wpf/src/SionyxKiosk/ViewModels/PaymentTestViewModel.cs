using System.Text.Encodings.Web;
using System.Text.Json;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Serilog;
using SionyxKiosk.Infrastructure;
using SionyxKiosk.Services;
using SionyxKiosk.Views.Dialogs;

namespace SionyxKiosk.ViewModels;

/// <summary>
/// For rent test screen only ("תשלום (בדיקה)" in the sidebar) - lets the
/// operator try several Nedarim charge-with-saved-token strategies one at a
/// time against a real saved card, and see the raw response from Nedarim
/// directly, instead of guessing blind from server logs. Calls the
/// /debugChargeToken endpoint on the payment bridge, which does NOT credit
/// any purchase - it only reports what Nedarim actually said.
///
/// Each strategy WILL attempt a real ₪1 charge against Nedarim's live
/// system (there is no sandbox) if the request is even accepted - keep
/// that in mind when clicking through them.
/// </summary>
public partial class PaymentTestViewModel : ObservableObject
{
    private static readonly ILogger Logger = Log.ForContext<PaymentTestViewModel>();
    private readonly FirebaseClient _firebase;
    private readonly OrganizationMetadataService _metadataService;
    private readonly string _userId;

    [ObservableProperty] private string _resultText = "בחר אסטרטגיה כדי לנסות אותה מול הכרטיס השמור.";
    [ObservableProperty] private bool _isBusy;
    [ObservableProperty] private string _lastStrategyLabel = "";
    [ObservableProperty] private string _tokefInput = "";

    public PaymentTestViewModel(FirebaseClient firebase, OrganizationMetadataService metadataService, string userId)
    {
        _firebase = firebase;
        _metadataService = metadataService;
        _userId = userId;
    }

    [RelayCommand]
    private void OpenIframeTokenTest()
    {
        var dialog = new PaymentTokenTestDialog(_metadataService, _firebase, _userId);
        dialog.ShowDialog();
    }

    public record StrategyOption(string Key, string Label, string Description);

    public List<StrategyOption> Strategies { get; } = new()
    {
        // Manage3.aspx variants removed: confirmed wrong credentials there,
        // and repeating them risks Nedarim's IP-ban counter ("נסיון X מתוך
        // 10... כתובת ה-IP תיחסם לשעה"). DebitCard/DebitKeva without a real
        // Tokef removed too: confirmed dead ends (CAPTCHA / "מבנה תוקף לא
        // תקין"). Only the two Tokef-required variants remain - fill in
        // TokefInput with the card's real expiry (MMYY) before trying these.
        new("debitcard_token_with_tokef", "DebitCard.aspx + Token + תוקף אמיתי",
            "GET, כתובת מתועדת בפורומים - חובה למלא תוקף אמיתי בשדה למעלה"),
        new("debitkeva_token_with_tokef", "DebitKeva.aspx + Token + תוקף אמיתי",
            "GET, endpoint ייעודי להוראת קבע - חובה למלא תוקף אמיתי בשדה למעלה"),
    };

    [RelayCommand]
    private async Task RunStrategyAsync(string strategyKey)
    {
        var strategy = Strategies.Find(s => s.Key == strategyKey);
        IsBusy = true;
        LastStrategyLabel = strategy?.Label ?? strategyKey;
        ResultText = $"שולח בקשה עם אסטרטגיה: {LastStrategyLabel}...";

        try
        {
            var result = await _firebase.CallFunctionAsync("debugChargeToken", new
            {
                orgId = _firebase.OrgId,
                strategy = strategyKey,
                tokef = string.IsNullOrWhiteSpace(TokefInput) ? null : TokefInput.Trim(),
            });

            if (!result.Success)
            {
                ResultText = $"שגיאת קריאה לשרת:\n{result.Error}";
                Logger.Warning("debugChargeToken call failed: {Error}", result.Error);
                return;
            }

            var data = (JsonElement)result.Data!;
            var options = new JsonSerializerOptions
            {
                WriteIndented = true,
                Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping,
            };
            var pretty = JsonSerializer.Serialize(data, options);
            ResultText = $"אסטרטגיה: {LastStrategyLabel}\n\n{pretty}";
            Logger.Information("debugChargeToken [{Strategy}] result: {Result}", strategyKey, pretty);
        }
        catch (Exception ex)
        {
            ResultText = $"חריגה: {ex.Message}";
            Logger.Error(ex, "RunStrategyAsync failed for {Strategy}", strategyKey);
        }
        finally
        {
            IsBusy = false;
        }
    }
}
