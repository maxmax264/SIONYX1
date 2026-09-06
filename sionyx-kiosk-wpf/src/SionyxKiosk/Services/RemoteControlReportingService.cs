using System.Diagnostics;
using System.IO;
using System.Text.Json;
using System.Text.RegularExpressions;
using Serilog;
using SionyxKiosk.Infrastructure;

namespace SionyxKiosk.Services;

/// <summary>
/// שני כלי שליטה מרחוק עצמאיים רצים על כל קיוסק:
///   - RustDesk: לשימוש יומיומי של מנהל הארגון (סיסמה שהוא קובע מהדשבורד שלו)
///   - AnyDesk: מיועד אך ורק למסטר (owner) - כלי נפרד לחלוטין, לא תלוי ב-RustDesk
/// שירות זה קורא את קבצי המידע המקומיים שנוצרו ע"י install-rustdesk.ps1/install-anydesk.ps1
/// (ID + סיסמה אקראית ראשונית), מדווח אותם ל-Firebase פעם אחת, ואז מאזין בזמן אמת
/// (SseListener, אותה תבנית כמו ForceLogoutService) לשינויי סיסמה מהדשבורד ומיישם אותם מיידית
/// דרך ה-CLI של כל כלי.
/// </summary>
public class RemoteControlReportingService
{
    private static readonly ILogger Logger = Log.ForContext<RemoteControlReportingService>();

    private const string RustDeskInfoFile = @"C:\ProgramData\SIONYX\rustdesk-info.txt";
    private const string AnyDeskInfoFile = @"C:\ProgramData\SIONYX\anydesk-info.txt";
    private const string TeamViewerInfoFile = @"C:\ProgramData\SIONYX\teamviewer-info.txt";
    private const string AeroAdminInfoFile = @"C:\ProgramData\SIONYX\aeroadmin-info.txt";
    private const string RustDeskExe = @"C:\Program Files\RustDesk\rustdesk.exe";
    private const string AnyDeskExe = @"C:\Program Files (x86)\AnyDesk\AnyDesk.exe";
    // Staged by install-teamviewer.ps1, NOT run continuously - see StartTeamViewerQuickSupport
    // for why this is launched on-demand instead of installed as an always-on Host service.
    private const string TeamViewerQsExe = @"C:\ProgramData\SIONYX\TeamViewerQS.exe";
    private const string TeamViewerQsInfoIni = @"C:\ProgramData\SIONYX\TeamViewerQS\tvinfo.ini";

    private readonly FirebaseClient _firebase;
    private SseListener? _rustDeskListener;
    private SseListener? _anyDeskListener;
    private SseListener? _refreshListener;
    private SseListener? _teamViewerLaunchListener;
    private string? _computerId;

    public RemoteControlReportingService(FirebaseClient firebase)
    {
        _firebase = firebase;
    }

    /// <summary>קריאה חד-פעמית באתחול האפליקציה, אחרי שהמשתמש/הקיוסק מאומת מול Firebase.</summary>
    public async Task InitializeAsync()
    {
        _computerId = DeviceInfo.GetDeviceId();

        await ReportCurrentInfoAsync();

        StartListening(_computerId);
    }

    /// <summary>קורא מחדש את קבצי ה-info של שני הכלים ומדווח ל-Firebase. נקרא גם
    /// באתחול וגם כשמתקבלת בקשת רענון מהדשבורד (remoteControl/refreshRequested) -
    /// מכסה מקרה של דיווח ראשוני שנכשל, או ID/סיסמה שהתחלפו (למשל אחרי התקנה מחדש).</summary>
    private async Task ReportCurrentInfoAsync()
    {
        if (_computerId == null) return;
        await ReportInitialInfoAsync("rustdesk", RustDeskInfoFile, "RustDesk", _computerId);
        await ReportInitialInfoAsync("anydesk", AnyDeskInfoFile, "AnyDesk", _computerId);
        // TeamViewer is NOT reported here - it isn't installed as an always-on
        // service, so there's no info file to read at startup. Its ID+password
        // only exist after a launchRequest triggers StartTeamViewerQuickSupport
        // below (see the listener in StartListening). Left the old file constant
        // in case a future version does stage a persistent info file.
        await ReportInitialInfoAsync("aeroadmin", AeroAdminInfoFile, "AeroAdmin", _computerId);
    }

    private async Task ReportInitialInfoAsync(string tool, string infoFilePath, string idLabel, string computerId)
    {
        try
        {
            if (!File.Exists(infoFilePath))
            {
                Logger.Debug("{Tool} info file not found ({Path}) - tool not installed on this machine yet", tool, infoFilePath);
                return;
            }

            var content = await File.ReadAllTextAsync(infoFilePath);
            var idMatch = Regex.Match(content, $@"{idLabel} ID:\s*(\S+)");
            var pwMatch = Regex.Match(content, $@"{idLabel} Password:\s*(\S+)");
            if (!idMatch.Success || !pwMatch.Success)
            {
                Logger.Warning("{Tool} info file malformed: {Path}", tool, infoFilePath);
                return;
            }

            // דיווח רק אם עוד לא דווח (או השתנה) - נמנע מכתיבה מיותרת בכל אתחול
            var path = $"computers/{computerId}/remoteControl/{tool}";
            var data = new Dictionary<string, object>
            {
                ["id"] = idMatch.Groups[1].Value,
                ["password"] = pwMatch.Groups[1].Value,
                ["reportedAt"] = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(),
            };
            var result = await _firebase.DbUpdateAsync(path, data);
            if (!result.Success)
            {
                Logger.Warning("{Tool} info FAILED to report to Firebase for computer {ComputerId}: {Error}", tool, computerId, result.Error);
                return;
            }
            Logger.Information("{Tool} info reported to Firebase for computer {ComputerId}", tool, computerId);
        }
        catch (Exception ex)
        {
            Logger.Error(ex, "Failed to report {Tool} info to Firebase", tool);
        }
    }

    private void StartListening(string computerId)
    {
        // מאזינים ל-setPassword (ערוץ פקודה, מוגן ב-Rules לפי הרשאה) ולא ל-password
        // (ערוץ דיווח-עצמי, פתוח לכל חבר ארגון מחובר) - כדי שדיווח הסיסמה הראשונית
        // שהותקנה לא ייתקל בחסימת הרשאות כשמחובר בקיוסק משתמש שאינו אדמין/מסטר
        _rustDeskListener = _firebase.DbListen(
            $"computers/{computerId}/remoteControl/rustdesk/setPassword",
            (eventType, data) => OnPasswordChanged(eventType, data, "rustdesk", RustDeskExe, SetRustDeskPassword));

        _anyDeskListener = _firebase.DbListen(
            $"computers/{computerId}/remoteControl/anydesk/setPassword",
            (eventType, data) => OnPasswordChanged(eventType, data, "anydesk", AnyDeskExe, SetAnyDeskPassword));

        _refreshListener = _firebase.DbListen(
            $"computers/{computerId}/remoteControl/refreshRequested",
            (eventType, data) => OnRefreshRequested(eventType, data));

        // דש-בורד לוחץ "הפעל TeamViewer" -> כותב timestamp כאן -> מפעילים
        // QuickSupport על הקיוסק ומדווחים בחזרה ID+סיסמה חדשה. לא Host קבוע -
        // ראו את ההערה ב-StartTeamViewerQuickSupport.
        _teamViewerLaunchListener = _firebase.DbListen(
            $"computers/{computerId}/remoteControl/teamviewer/launchRequest",
            (eventType, data) => OnTeamViewerLaunchRequested(eventType, data));
    }

    private void OnRefreshRequested(string eventType, JsonElement? data)
    {
        if (eventType != "put" || data == null) return;
        if (data.Value.ValueKind != JsonValueKind.Number) return;
        Logger.Information("Remote-control refresh requested from dashboard - re-reporting current info");
        _ = Task.Run(async () =>
        {
            try { await ReportCurrentInfoAsync(); }
            catch (Exception ex) { Logger.Warning(ex, "Refresh-triggered re-report failed"); }
        });
    }

    private void OnPasswordChanged(string eventType, JsonElement? data, string tool, string exePath, Action<string, string> applyFn)
    {
        try
        {
            if (eventType != "put" || data == null) return;
            if (data.Value.ValueKind != JsonValueKind.String) return;
            var newPassword = data.Value.GetString();
            if (string.IsNullOrWhiteSpace(newPassword)) return;
            if (!File.Exists(exePath))
            {
                Logger.Warning("{Tool} not installed on this machine - ignoring remote password update", tool);
                return;
            }

            applyFn(exePath, newPassword);
            Logger.Information("{Tool} password updated remotely (real-time sync)", tool);

            // מעדכן את שדה הדיווח-העצמי כדי שהדשבורד יציג את הסיסמה החדשה בפועל
            _ = Task.Run(async () =>
            {
                try
                {
                    if (_computerId == null) return;
                    var path = $"computers/{_computerId}/remoteControl/{tool}";
                    await _firebase.DbUpdateAsync(path, new Dictionary<string, object>
                    {
                        ["password"] = newPassword,
                        ["reportedAt"] = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(),
                    });
                }
                catch (Exception ex) { Logger.Warning(ex, "Failed to sync applied {Tool} password back to report field", tool); }
            });
        }
        catch (Exception ex)
        {
            Logger.Error(ex, "Failed to apply remote password change for {Tool}", tool);
        }
    }

    private void OnTeamViewerLaunchRequested(string eventType, JsonElement? data)
    {
        if (eventType != "put" || data == null) return;
        if (data.Value.ValueKind != JsonValueKind.Number) return;
        Logger.Information("TeamViewer QuickSupport launch requested from dashboard");
        _ = Task.Run(async () =>
        {
            try { await StartTeamViewerQuickSupportAsync(); }
            catch (Exception ex) { Logger.Warning(ex, "TeamViewer QuickSupport launch failed"); }
        });
    }

    /// <summary>
    /// מפעיל QuickSupport לפי דרישה במקום להתקין TeamViewer Host כשירות רקע קבוע.
    /// הסיבה: unattended access קבוע דרך חשבון חינמי על כמה קיוסקים הוא בדיוק
    /// דפוס השימוש ש-TeamViewer מזהה כ"commercial use" וחוסם - ראו את הדיון
    /// בזיכרון הפרויקט. הפעלה זמנית לפי בקשה, session בודד בכל פעם, נראית הרבה
    /// יותר כמו תמיכה מזדמנת לגיטימית.
    ///
    /// TODO לא סופי: פורמט tvinfo.ini עדיין לא אושר בפועל (המשתמש עדיין לא שלח
    /// את התוכן שלו) - ה-regex למטה הוא ניחוש סביר על סמך תיעוד קהילתי, לא
    /// מאומת. אם ה-parse נכשל, זה יירשם ב-log עם תוכן הקובץ המלא כדי שנוכל
    /// לתקן את ה-regex בלי לגשת שוב למחשב.
    /// </summary>
    private async Task StartTeamViewerQuickSupportAsync()
    {
        if (!File.Exists(TeamViewerQsExe))
        {
            Logger.Warning("TeamViewerQS.exe not staged on this machine ({Path}) - install-teamviewer.ps1 may not have run", TeamViewerQsExe);
            return;
        }

        // מוחקים קובץ מידע קודם כדי לא להזדהם ID/סיסמה ישנים אם ה-launch הנוכחי ייכשל
        try { if (File.Exists(TeamViewerQsInfoIni)) File.Delete(TeamViewerQsInfoIni); } catch { /* לא קריטי */ }

        var psi = new ProcessStartInfo(TeamViewerQsExe)
        {
            UseShellExecute = true, // QuickSupport צריך חלון גרפי גלוי על הקיוסק
            WorkingDirectory = Path.GetDirectoryName(TeamViewerQsExe),
        };
        Process.Start(psi);

        // ממתינים ל-handshake מול שרתי TeamViewer וליצירת tvinfo.ini - יכול לקחת
        // כמה שניות, מנסים כמו בתבנית של AnyDesk/RustDesk
        string? content = null;
        for (var i = 0; i < 10 && content == null; i++)
        {
            await Task.Delay(2000);
            try
            {
                if (File.Exists(TeamViewerQsInfoIni))
                {
                    content = await File.ReadAllTextAsync(TeamViewerQsInfoIni);
                }
            }
            catch { /* ה-קובץ עוד נכתב, ננסה שוב */ }
        }

        if (content == null)
        {
            Logger.Warning("tvinfo.ini never appeared after launching TeamViewerQS - giving up for this request");
            return;
        }

        // TODO: לאמת מול תוכן אמיתי - ניחוש נוכחי: "ID=123456789" ו-"Password=xxxxxxxx" בשורות נפרדות
        var idMatch = Regex.Match(content, @"ID\s*=\s*(\S+)", RegexOptions.IgnoreCase);
        var pwMatch = Regex.Match(content, @"Password\s*=\s*(\S+)", RegexOptions.IgnoreCase);
        if (!idMatch.Success || !pwMatch.Success)
        {
            Logger.Warning("tvinfo.ini format did not match expected pattern - raw content: {Content}", content);
            return;
        }

        if (_computerId == null) return;
        var path = $"computers/{_computerId}/remoteControl/teamviewer";
        var result = await _firebase.DbUpdateAsync(path, new Dictionary<string, object>
        {
            ["id"] = idMatch.Groups[1].Value,
            ["password"] = pwMatch.Groups[1].Value,
            ["reportedAt"] = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(),
        });
        if (!result.Success)
        {
            Logger.Warning("TeamViewer QuickSupport info FAILED to report to Firebase: {Error}", result.Error);
            return;
        }
        Logger.Information("TeamViewer QuickSupport ID+password reported to Firebase for computer {ComputerId}", _computerId);
    }

    private static void SetRustDeskPassword(string exePath, string password)
    {
        RunProcess(exePath, $"--password {password}");
    }

    private static void SetAnyDeskPassword(string exePath, string password)
    {
        // AnyDesk מקבל סיסמה דרך stdin, לא כארגומנט גלוי בשורת הפקודה
        var psi = new ProcessStartInfo(exePath, "--set-password")
        {
            RedirectStandardInput = true,
            UseShellExecute = false,
            CreateNoWindow = true,
        };
        using var process = Process.Start(psi);
        process?.StandardInput.WriteLine(password);
        process?.StandardInput.Close();
        process?.WaitForExit(10000);
    }

    private static void RunProcess(string exePath, string arguments)
    {
        var psi = new ProcessStartInfo(exePath, arguments)
        {
            UseShellExecute = false,
            CreateNoWindow = true,
        };
        using var process = Process.Start(psi);
        process?.WaitForExit(10000);
    }

    public void StopListening()
    {
        _rustDeskListener?.Stop();
        _anyDeskListener?.Stop();
        _refreshListener?.Stop();
        _teamViewerLaunchListener?.Stop();
    }
}
