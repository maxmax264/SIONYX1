using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using SionyxKiosk.Services;

namespace SionyxKiosk.ViewModels;

/// <summary>Auth ViewModel: login, register, password reset.</summary>
public partial class AuthViewModel : ObservableObject
{
    private readonly AuthService _auth;
    private readonly OrganizationMetadataService? _metadataService;

    [ObservableProperty] private string _phone = "";
    [ObservableProperty] private string _password = "";
    [ObservableProperty] private string _firstName = "";
    [ObservableProperty] private string _lastName = "";
    [ObservableProperty] private string _email = "";
    [ObservableProperty] private string _errorMessage = "";
    [ObservableProperty] private bool _isLoading;
    [ObservableProperty] private bool _isLoginMode = true;
    [ObservableProperty] private string _forgotPasswordInfo = "";
    [ObservableProperty] private string _backgroundImageUrl = "";
    [ObservableProperty] private bool _hasBackgroundImage;
    [ObservableProperty] private double _bgOpacity = 0.55;
    [ObservableProperty] private string _bgStretch = "UniformToFill";
    [ObservableProperty] private System.Windows.Media.ImageSource? _backgroundImageSource;

    // authDesign properties
    [ObservableProperty] private string _overlayColor1 = "#6366F1";
    [ObservableProperty] private string _buttonColor = "";
    [ObservableProperty] private string _overlayColor2 = "#8B5CF6";
    [ObservableProperty] private string _brandSubtitle = "ניהול מחשבים חכם";
    [ObservableProperty] private string _welcomeText = "ברוכים הבאים";
    [ObservableProperty] private string _welcomeSubtext = "התחבר לחשבון שלך";
    [ObservableProperty] private bool _showRegister = true;
    [ObservableProperty] private bool _cleanMode = false;
    [ObservableProperty] private double _formX = 50;
    [ObservableProperty] private double _formY = 50;
    [ObservableProperty] private double _formWidth = 480;
    public double FormXPixels => Math.Max(0, ((100.0 - FormX) / 100.0) * (System.Windows.SystemParameters.PrimaryScreenWidth - FormWidth));
    public double FormYPixels => Math.Max(0, FormY / 100.0 * (System.Windows.SystemParameters.PrimaryScreenHeight - 700));
    public System.Windows.Thickness FormMargin => new System.Windows.Thickness(FormXPixels, FormYPixels, 0, 0);
    partial void OnFormXChanged(double value) { Serilog.Log.Information("[Form] X={X} ScreenW={SW} FormW={FW} => Pixels={P}", FormX, System.Windows.SystemParameters.PrimaryScreenWidth, FormWidth, FormXPixels); OnPropertyChanged(nameof(FormXPixels)); OnPropertyChanged(nameof(FormMargin)); }
    partial void OnFormYChanged(double value) { OnPropertyChanged(nameof(FormYPixels)); OnPropertyChanged(nameof(FormMargin)); }
    [ObservableProperty] private System.Windows.Media.Brush _overlayGradient = new System.Windows.Media.LinearGradientBrush(
        (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString("#6366F1"),
        (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString("#8B5CF6"),
        45);
    [ObservableProperty] private System.Windows.Media.Brush _buttonGradient = new System.Windows.Media.SolidColorBrush(
        (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString("#6366F1"));

    /// <summary>Dynamic button text that changes during loading.</summary>
    public string LoginButtonText => IsLoading ? "מתחבר..." : "התחבר";
    public string RegisterButtonText => IsLoading ? "נרשם..." : "הירשם";

    partial void OnIsLoadingChanged(bool value)
    {
        OnPropertyChanged(nameof(LoginButtonText));
        OnPropertyChanged(nameof(RegisterButtonText));
    }

    public event Action? LoginSucceeded;
    public event Action? RegistrationSucceeded;

    public AuthViewModel(AuthService auth, OrganizationMetadataService? metadataService = null)
    {
        _auth = auth;
        _metadataService = metadataService;
        _ = LoadBackgroundAsync();
        _ = StartRefreshListenerAsync();
    }

    public async Task ReloadBackgroundAsync() => await LoadBackgroundAsync();

    private async Task StartRefreshListenerAsync()
    {
        if (_metadataService == null) return;
        try
        {
            var config = SionyxKiosk.Infrastructure.FirebaseConfig.Load();
            using var http = new System.Net.Http.HttpClient();
            http.Timeout = System.Threading.Timeout.InfiniteTimeSpan;
            var url = $"{config.DatabaseUrl}/organizations/{config.OrgId}/metadata/kioskRefreshAt.json";
            string? lastVal = null;
            while (true)
            {
                try
                {
                    var json = await http.GetStringAsync(url);
                    var val = json.Trim().Trim('"');
                    if (lastVal != null && val != lastVal)
                    {
                        Serilog.Log.Information("[BG] Refresh triggered from dashboard");
                        await ReloadBackgroundAsync();
                    }
                    lastVal = val;
                }
                catch { }
                await System.Threading.Tasks.Task.Delay(3000);
            }
        }
        catch (Exception ex) { Serilog.Log.Error(ex, "[BG] RefreshListener failed"); }
    }

    private async Task LoadBackgroundAsync()
    {
        if (_metadataService == null) { Serilog.Log.Warning("[BG] metadataService is null"); return; }
        try
        {
            var result = await _metadataService.GetKioskBackgroundAsync();
            Serilog.Log.Information("[BG] IsSuccess={S} dataType={D}", result.IsSuccess, result.Data?.GetType().Name ?? "null");
            if (result.IsSuccess && result.Data is { } data)
            {
                var type = data.GetType();
                var enabled = type.GetProperty("enabled")?.GetValue(data) is bool b && b;
                var url = type.GetProperty("url")?.GetValue(data)?.ToString() ?? "";
                Serilog.Log.Information("[BG] enabled={E} urlLen={L}", enabled, url.Length);
                if (enabled && !string.IsNullOrWhiteSpace(url))
                {
                    BackgroundImageUrl = url;
                    HasBackgroundImage = true;
                    try {
                        System.Windows.Application.Current.Dispatcher.Invoke(() => {
                            var bmp = new System.Windows.Media.Imaging.BitmapImage();
                            bmp.BeginInit();
                            if (url.StartsWith("data:image")) {
                                var b64 = url.Substring(url.IndexOf(',')+1);
                                var bytes = System.Convert.FromBase64String(b64);
                                bmp.StreamSource = new System.IO.MemoryStream(bytes);
                                bmp.CacheOption = System.Windows.Media.Imaging.BitmapCacheOption.OnLoad;
                            } else {
                                bmp.UriSource = new Uri(url, UriKind.Absolute);
                                bmp.CacheOption = System.Windows.Media.Imaging.BitmapCacheOption.OnLoad;
                            }
                            bmp.EndInit();
                            BackgroundImageSource = bmp;
                        });
                    } catch (Exception ex2) { Serilog.Log.Error(ex2, "[BG] BitmapImage failed"); }
                    try {
                        using var http2 = new System.Net.Http.HttpClient();
                        var cfg = SionyxKiosk.Infrastructure.FirebaseConfig.Load();
                        var durl = $"{cfg.DatabaseUrl}/organizations/{cfg.OrgId}/metadata/kioskDesign.json";
                        var djson = await http2.GetStringAsync(durl);
                        if (djson != "null" && !string.IsNullOrEmpty(djson)) {
                            var d = System.Text.Json.JsonDocument.Parse(djson).RootElement;
                            System.Windows.Application.Current.Dispatcher.Invoke(() => {
                                if (d.TryGetProperty("opacity", out var op)) BgOpacity = op.GetDouble();
                                if (d.TryGetProperty("stretch", out var st)) BgStretch = st.GetString() ?? "UniformToFill";
                            });
                        }
                    } catch { }
                    Serilog.Log.Information("[BG] Background set OK, HasBg={H}", HasBackgroundImage);
                    await LoadAuthDesignAsync();
                    return;
                }
            }
        }
        catch (Exception ex) { Serilog.Log.Error(ex, "[BG] Exception loading background"); }
        BackgroundImageUrl = "";
        HasBackgroundImage = false;
        Serilog.Log.Warning("[BG] No background set");
        await LoadAuthDesignAsync();
    }

    private static bool IsValidPhone(string phone)
    {
        var digits = phone.Replace("-", "").Replace(" ", "").Trim();
        return digits.Length >= 9 && digits.Length <= 12 && digits.All(char.IsDigit);
    }

    [RelayCommand]
    private async Task LoginAsync()
    {
        if (string.IsNullOrWhiteSpace(Phone) || string.IsNullOrWhiteSpace(Password))
        {
            ErrorMessage = "אנא מלא את כל השדות";
            return;
        }

        if (!IsValidPhone(Phone))
        {
            ErrorMessage = "מספר טלפון לא תקין";
            return;
        }

        IsLoading = true;
        ErrorMessage = "";

        var result = await _auth.LoginAsync(Phone, Password);
        IsLoading = false;

        if (result.IsSuccess)
            LoginSucceeded?.Invoke();
        else
            ErrorMessage = result.Error ?? "שגיאת התחברות";
    }

    [RelayCommand]
    private async Task RegisterAsync()
    {
        if (string.IsNullOrWhiteSpace(Phone) || string.IsNullOrWhiteSpace(Password) ||
            string.IsNullOrWhiteSpace(FirstName) || string.IsNullOrWhiteSpace(LastName))
        {
            ErrorMessage = "אנא מלא את כל השדות";
            return;
        }

        if (!IsValidPhone(Phone))
        {
            ErrorMessage = "מספר טלפון לא תקין";
            return;
        }

        if (Password.Length < 6)
        {
            ErrorMessage = "הסיסמה חייבת להכיל לפחות 6 תווים";
            return;
        }

        IsLoading = true;
        ErrorMessage = "";

        var result = await _auth.RegisterAsync(Phone, Password, FirstName, LastName, Email);
        IsLoading = false;

        if (result.IsSuccess)
            RegistrationSucceeded?.Invoke();
        else
            ErrorMessage = result.Error ?? "שגיאת הרשמה";
    }

    public void ResetForm()
    {
        Phone = "";
        Password = "";
        FirstName = "";
        LastName = "";
        Email = "";
        ErrorMessage = "";
        ForgotPasswordInfo = "";
        IsLoginMode = true;
    }

    [RelayCommand]
    private void ToggleMode()
    {
        IsLoginMode = !IsLoginMode;
        ErrorMessage = "";
        ForgotPasswordInfo = "";
    }

    [RelayCommand]
    private async Task ForgotPasswordAsync()
    {
        if (_metadataService == null)
        {
            ForgotPasswordInfo = "לא ניתן לטעון פרטי קשר. פנה למנהל המערכת.";
            return;
        }

        IsLoading = true;
        try
        {
            var result = await _metadataService.GetAdminContactAsync();
            if (result.IsSuccess && result.Data is { } contact)
            {
                var type = contact.GetType();
                var phone = type.GetProperty("phone")?.GetValue(contact)?.ToString() ?? "";
                var email = type.GetProperty("email")?.GetValue(contact)?.ToString() ?? "";

                var info = "לאיפוס סיסמה פנה למנהל:";
                if (!string.IsNullOrEmpty(phone)) info += $"\n📞 {phone}";
                if (!string.IsNullOrEmpty(email)) info += $"\n✉️ {email}";
                ForgotPasswordInfo = info;
            }
            else
            {
                ForgotPasswordInfo = "פנה למנהל המערכת לאיפוס סיסמה.";
            }
        }
        catch
        {
            ForgotPasswordInfo = "פנה למנהל המערכת לאיפוס סיסמה.";
        }
        finally
        {
            IsLoading = false;
        }
    }

    private async Task LoadAuthDesignAsync()
    {
        try
        {
            var cfg = SionyxKiosk.Infrastructure.FirebaseConfig.Load();
            using var http = new System.Net.Http.HttpClient();
            var url = $"{cfg.DatabaseUrl}/organizations/{cfg.OrgId}/metadata/authDesign.json";
            var response = await http.GetAsync(url);
            if (!response.IsSuccessStatusCode) { Serilog.Log.Warning("[Design] authDesign HTTP {S}", response.StatusCode); return; }
            var json = await response.Content.ReadAsStringAsync();
            if (json == "null" || string.IsNullOrEmpty(json)) return;
            var d = System.Text.Json.JsonDocument.Parse(json).RootElement;
            System.Windows.Application.Current.Dispatcher.Invoke(() =>
            {
                if (d.TryGetProperty("overlayColor1", out var c1)) OverlayColor1 = (c1.GetString() ?? "#6366F1").Trim();
                if (d.TryGetProperty("overlayColor2", out var c2)) OverlayColor2 = (c2.GetString() ?? "#8B5CF6").Trim();
                if (d.TryGetProperty("buttonColor", out var bc)) { var bcStr = bc.GetString(); if (!string.IsNullOrEmpty(bcStr)) ButtonColor = bcStr.Trim(); }
                if (d.TryGetProperty("brandSubtitle", out var bs)) BrandSubtitle = bs.GetString() ?? "";
                if (d.TryGetProperty("welcomeText", out var wt)) WelcomeText = wt.GetString() ?? "";
                if (d.TryGetProperty("welcomeSubtext", out var ws)) WelcomeSubtext = ws.GetString() ?? "";
                if (d.TryGetProperty("showRegister", out var sr)) ShowRegister = sr.GetBoolean();
                if (d.TryGetProperty("formX", out var fx)) FormX = fx.GetDouble();
                if (d.TryGetProperty("formY", out var fy)) FormY = fy.GetDouble();
                if (d.TryGetProperty("formWidth", out var fw)) FormWidth = fw.GetDouble();
                if (d.TryGetProperty("cleanMode", out var cm)) { 
                    CleanMode = cm.GetBoolean(); 
                    Serilog.Log.Information("[Design] CleanMode updated to {V}", CleanMode); 
                }

                // עדכן את הגרדיאנט
                try
                {
                    var oc1 = (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString(OverlayColor1);
                    var oc2 = (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString(OverlayColor2);
                    OverlayGradient = new System.Windows.Media.LinearGradientBrush(oc1, oc2, 45);
                }
                catch { }
                try
                {
                    var btnCol = !string.IsNullOrEmpty(ButtonColor) ? ButtonColor : OverlayColor1;
                    var btnColor = (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString(btnCol);
                    ButtonGradient = new System.Windows.Media.SolidColorBrush(btnColor);
                }
                catch { }
            });
            Serilog.Log.Information("[Design] authDesign loaded OK");
        }
        catch (Exception ex) { Serilog.Log.Error(ex, "[Design] Failed to load authDesign"); }
    }

    /// <summary>Called by App when auto-login succeeds.</summary>
    public void TriggerAutoLogin() => LoginSucceeded?.Invoke();
}
