using System.Text.Json;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Serilog;
using SionyxKiosk.Infrastructure;

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

    [ObservableProperty] private string _resultText = "בחר אסטרטגיה כדי לנסות אותה מול הכרטיס השמור.";
    [ObservableProperty] private bool _isBusy;
    [ObservableProperty] private string _lastStrategyLabel = "";

    public PaymentTestViewModel(FirebaseClient firebase)
    {
        _firebase = firebase;
    }

    public record StrategyOption(string Key, string Label, string Description);

    public List<StrategyOption> Strategies { get; } = new()
    {
        new("manage3_v1", "Manage3 v1 (המקורי)", "POST ל-Reports/Manage3.aspx, MosadNumber/ApiPassword"),
        new("manage3_v2", "Manage3 v2", "POST ל-Reports/Manage3.aspx, Mosad/ApiValid"),
        new("manage3_v3", "Manage3 v3", "POST ל-Reports/Manage3.aspx, MosadId/Token"),
        new("debitcard_token", "DebitCard.aspx + Token", "GET, כתובת מתועדת בפורומים, בלי ApiValid"),
        new("debitcard_token_apivalid", "DebitCard.aspx + Token + ApiValid", "אותו דבר, עם ApiValid מצורף"),
        new("debitkeva_token", "DebitKeva.aspx + Token", "GET, endpoint ייעודי להוראת קבע"),
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
            });

            if (!result.Success)
            {
                ResultText = $"שגיאת קריאה לשרת:\n{result.Error}";
                Logger.Warning("debugChargeToken call failed: {Error}", result.Error);
                return;
            }

            var data = (JsonElement)result.Data!;
            var options = new JsonSerializerOptions { WriteIndented = true };
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
