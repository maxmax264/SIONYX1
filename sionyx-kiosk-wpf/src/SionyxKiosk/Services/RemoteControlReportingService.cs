using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text.Json;
using System.Text.RegularExpressions;
using System.Threading;
using System.Windows.Automation;
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
    private const string TeamViewerUiDebugFile = @"C:\ProgramData\SIONYX\teamviewer-ui-debug.txt";

    // תיקיית ההתקנה (RemoteControlDir ב-Package.wxs) - הסקריפטים האלה נשארים
    // על הדיסק לצמיתות אחרי ההתקנה, ליד קובץ ה-exe של האפליקציה עצמה, אז
    // אפשר להריץ אותם שוב מתוך האפליקציה בזמן ריצה (לא רק מה-MSI) לצורך
    // ריפוי-עצמי - ראו EnsureAgentsStagedAsync.
    private static readonly string RemoteControlScriptsDir = Path.Combine(AppContext.BaseDirectory, "RemoteControl");
    private const int AnyDeskIdRetryIntervalMinutes = 5;
    private const int AeroAdminSetupRetryIntervalMinutes = 5;

    private readonly FirebaseClient _firebase;
    private readonly AeroAdminSetupService _aeroAdminSetup;
    private SseListener? _rustDeskListener;
    private SseListener? _anyDeskListener;
    private SseListener? _refreshListener;
    private SseListener? _teamViewerLaunchListener;
    private Timer? _anyDeskIdRetryTimer;
    private Timer? _aeroAdminSetupRetryTimer;
    private string? _computerId;

    public RemoteControlReportingService(FirebaseClient firebase, AeroAdminSetupService aeroAdminSetup)
    {
        _firebase = firebase;
        _aeroAdminSetup = aeroAdminSetup;
    }

    /// <summary>קריאה חד-פעמית באתחול האפליקציה, אחרי שהמשתמש/הקיוסק מאומת מול Firebase.</summary>
    public async Task InitializeAsync()
    {
        _computerId = DeviceInfo.GetDeviceId();

        // מנגנון ריפוי-עצמי: קיוסקים שהותקנו לפני שהתמיכה בכלי מסוים נוספה
        // (או שהותקנו לפני שהוסר "NOT Installed" ב-Package.wxs) לא יקבלו אותו
        // רק מעדכון רגיל - בודק מה חסר בפועל ומריץ את הסקריפט המתאים.
        try { await EnsureAgentsStagedAsync(); }
        catch (Exception ex) { Logger.Warning(ex, "Remote-control agent self-heal failed at startup"); }

        // מנסה להגדיר את AeroAdmin פעם אחת אם עוד לא הוגדר (ראה AeroAdminSetupService -
        // לא עושה כלום אם aeroadmin-info.txt כבר קיים או שהכלי לא מותקן על המכונה).
        // BUG שנמצא ותוקן: הניסיון הזה היה *חד-פעמי בלבד* - בניגוד ל-AnyDesk
        // שיש לו טיימר ניסיון-חוזר (_anyDeskIdRetryTimer, מטה), ל-AeroAdmin לא
        // היה שום ריפוי-עצמי נוסף. אם הניסיון הראשון נכשל מכל סיבה חולפת (חלון
        // ה-EULA/רישוי בהפעלה ראשונה שעדיין לא אושר, ה-exe עדיין לא סיים להתקין
        // ע"י EnsureAgentsStagedAsync שרץ ממש לפני זה, timing של עליית החלון וכו') -
        // ה-InfoFile לעולם לא נכתב, אז ReportCurrentInfoAsync רואה "קובץ לא קיים"
        // ומדווח לדשבורד "לא הותקן" לצמיתות, עד הפעלה מחדש של האפליקציה או
        // לחיצה ידנית על "רענן" בדשבורד. זו הסיבה המרכזית שAeroAdmin (וגם
        // TeamViewer בדפוס אחר - ראו ההערה שם) נראים "קיימים בקוד" אבל בפועל
        // אף פעם לא שולחים נתונים על קיוסקים מסוימים. התיקון: טיימר ניסיון-חוזר
        // תקופתי (_aeroAdminSetupRetryTimer, מטה) - EnsureConfiguredAsync כבר
        // אידמפוטנטי (מדלג אם aeroadmin-info.txt קיים), אז קריאה חוזרת בטוחה.
        try { await _aeroAdminSetup.EnsureConfiguredAsync(); }
        catch (Exception ex) { Logger.Warning(ex, "AeroAdmin one-time setup failed at startup"); }

        await ReportCurrentInfoAsync();

        StartListening(_computerId);

        // AnyDesk ID יכול להיתקע על "0" (פילטר רשת חוסם TLS ל-relay שלו) -
        // בודקים כל כמה דקות אם המצב השתנה (למשל אחרי שמנהל הרשת פתח חריגה),
        // בלי לחכות להפעלה מחדש של הקיוסק.
        _anyDeskIdRetryTimer = new Timer(
            _ => _ = RetryAnyDeskIdIfStuckAsync(),
            null,
            TimeSpan.FromMinutes(AnyDeskIdRetryIntervalMinutes),
            TimeSpan.FromMinutes(AnyDeskIdRetryIntervalMinutes));

        // תיקון הבאג שנמצא: ניסיון חוזר תקופתי ל-AeroAdmin, אותה תבנית בדיוק
        // כמו AnyDesk מעלה. EnsureConfiguredAsync מחזיר מיידית בלי לעשות כלום
        // אם aeroadmin-info.txt כבר קיים (ראה AeroAdminSetupService) - אז ברגע
        // שניסיון אחד מצליח, כל שאר הטיקים הם no-op זול. אם עדיין לא הצליח,
        // מנסים שוב ומדווחים לפיירבייס במקום לחכות להפעלה מחדש/לחיצת "רענן".
        _aeroAdminSetupRetryTimer = new Timer(
            _ => _ = RetryAeroAdminSetupIfNotConfiguredAsync(),
            null,
            TimeSpan.FromMinutes(AeroAdminSetupRetryIntervalMinutes),
            TimeSpan.FromMinutes(AeroAdminSetupRetryIntervalMinutes));
    }

    private async Task RetryAeroAdminSetupIfNotConfiguredAsync()
    {
        try
        {
            if (File.Exists(AeroAdminInfoFile)) return; // כבר הוגדר בהצלחה - אין מה לעשות
            Logger.Information("AeroAdmin still not configured - periodic retry attempt");
            await _aeroAdminSetup.EnsureConfiguredAsync();
            if (File.Exists(AeroAdminInfoFile) && _computerId != null)
            {
                await ReportInitialInfoAsync("aeroadmin", AeroAdminInfoFile, "AeroAdmin", _computerId);
            }
        }
        catch (Exception ex)
        {
            Logger.Debug(ex, "Periodic AeroAdmin setup retry failed (non-fatal, will try again next interval)");
        }
    }

    /// <summary>בודק אילו מכלי השליטה מרחוק חסרים בפועל על המכונה (exe לא קיים)
    /// ומריץ מחדש את סקריפט ההתקנה שלהם מתוך התיקייה שהותקנה עם האפליקציה
    /// (RemoteControlDir) - בלי לחכות ל-MSI חדש/reinstall מלא. כל סקריפט
    /// אידמפוטנטי (בודק Test-Path/Get-Service בעצמו), אז הרצה חוזרת בטוחה.
    /// הערה: מניח שתהליך האפליקציה רץ בהרשאות מספיקות להתקנת שירותים/תוכנה
    /// (כמו KioskPolicyService שכבר עושה פעולות ברמת-מערכת) - אם זה לא המצב
    /// בפועל, ההרצה תיכשל בשקט ותתועד ב-Warning; יש לוודא ידנית בבדיקה ראשונה.
    /// RustDesk לא נכלל בכוונה - מושבת גלובלית להתקנות חדשות (ראו Package.wxs).</summary>
    private async Task EnsureAgentsStagedAsync()
    {
        await RunInstallScriptIfMissingAsync("install-anydesk.ps1", AnyDeskExe, "AnyDesk");
        await RunInstallScriptIfMissingAsync("install-teamviewer.ps1", TeamViewerQsExe, "TeamViewer QuickSupport");
        await RunInstallScriptIfMissingAsync("install-aeroadmin.ps1", AeroAdminSetupService.ExePath, "AeroAdmin");
    }

    private async Task RunInstallScriptIfMissingAsync(string scriptFileName, string expectedExePath, string label)
    {
        if (File.Exists(expectedExePath))
        {
            return; // כבר מותקן - שום דבר לעשות
        }

        var scriptPath = Path.Combine(RemoteControlScriptsDir, scriptFileName);
        if (!File.Exists(scriptPath))
        {
            Logger.Debug("{Label} self-heal: script not found at {Path} (older build without this file?)", label, scriptPath);
            return;
        }

        Logger.Information("{Label} not found on this machine ({ExePath}) - running {Script} to self-heal", label, expectedExePath, scriptFileName);
        try
        {
            var psi = new ProcessStartInfo("powershell.exe",
                $"-NoProfile -ExecutionPolicy Bypass -File \"{scriptPath}\"")
            {
                UseShellExecute = false,
                CreateNoWindow = true,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
            };
            using var process = Process.Start(psi);
            if (process == null)
            {
                Logger.Warning("{Label} self-heal: failed to start powershell.exe for {Script}", label, scriptFileName);
                return;
            }

            var stdout = await process.StandardOutput.ReadToEndAsync();
            var stderr = await process.StandardError.ReadToEndAsync();
            await process.WaitForExitAsync();

            if (process.ExitCode != 0 || !File.Exists(expectedExePath))
            {
                Logger.Warning("{Label} self-heal via {Script} did not result in {ExePath} existing (exit code {Code}). This usually means the app process lacks the rights this script needs (installing a service / writing to Program Files). Output: {Stdout} {Stderr}",
                    label, scriptFileName, expectedExePath, process.ExitCode, stdout, stderr);
                return;
            }

            Logger.Information("{Label} self-heal via {Script} succeeded", label, scriptFileName);
        }
        catch (Exception ex)
        {
            Logger.Error(ex, "{Label} self-heal via {Script} threw an exception", label, scriptFileName);
        }
    }

    /// <summary>קורא ל-RemoteControlReportingService פעם בכמה דקות אם ה-ID האחרון
    /// שדווח ל-Firebase הוא "0" (חסימת רשת) - ומנסה שוב ישירות מול ה-exe בלי
    /// להריץ מחדש את כל סקריפט ההתקנה. אם התקבל ID אמיתי (למשל אחרי שמנהל
    /// הרשת פתח חריגה ל-AnyDesk), מעדכן את קובץ ה-info המקומי ומדווח ל-Firebase.</summary>
    private async Task RetryAnyDeskIdIfStuckAsync()
    {
        try
        {
            if (_computerId == null || !File.Exists(AnyDeskInfoFile) || !File.Exists(AnyDeskExe)) return;

            var content = await File.ReadAllTextAsync(AnyDeskInfoFile);
            var idMatch = Regex.Match(content, @"AnyDesk ID:\s*(\S+)");
            if (!idMatch.Success) return;
            var currentId = idMatch.Groups[1].Value;
            if (currentId != "0" && !string.IsNullOrWhiteSpace(currentId)) return; // כבר יש ID תקין - אין מה לעשות

            var psi = new ProcessStartInfo(AnyDeskExe, "--get-id")
            {
                UseShellExecute = false,
                CreateNoWindow = true,
                RedirectStandardOutput = true,
            };
            using var process = Process.Start(psi);
            if (process == null) return;
            var newId = (await process.StandardOutput.ReadToEndAsync()).Trim();
            await process.WaitForExitAsync();

            if (string.IsNullOrWhiteSpace(newId) || newId == "0" || newId == currentId) return; // עדיין תקוע/לא השתנה

            Logger.Information("AnyDesk ID resolved on retry (was stuck at '0') - now {NewId}", newId);
            var updatedContent = Regex.Replace(content, @"AnyDesk ID:\s*\S+", $"AnyDesk ID:       {newId}");
            await File.WriteAllTextAsync(AnyDeskInfoFile, updatedContent);

            await _firebase.DbUpdateAsync($"computers/{_computerId}/remoteControl/anydesk", new Dictionary<string, object>
            {
                ["id"] = newId,
                ["reportedAt"] = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(),
            });
        }
        catch (Exception ex)
        {
            Logger.Debug(ex, "Periodic AnyDesk ID retry failed (non-fatal, will try again next interval)");
        }
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
        //
        // AeroAdmin: unlike RustDesk/AnyDesk, this file is written by
        // AeroAdminSetupService via UI Automation (no CLI exists for AeroAdmin -
        // see that class's comment), triggered once from InitializeAsync/refresh
        // above. By the time we get here it should already exist if setup
        // succeeded; this call just reports whatever is currently on disk.
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
            try
            {
                // כפתור "רענן" הוא גם הזדמנות שנייה לריפוי-עצמי - אם קיוסק
                // ישן מתקין עדכון בלי אחד מהכלים (למשל אחרי שהם נוספו לאחר
                // שהמכונה כבר הותקנה), הרענון מזהה ומתקין את מה שחסר.
                await EnsureAgentsStagedAsync();
                // אם AeroAdmin עוד לא הוגדר, או שה-PIN שלו התחדש מאז הדיווח
                // האחרון (נפוץ בכלים כאלה) - "רענן" קורא תמיד מחדש, בניגוד
                // ל-EnsureConfiguredAsync שמדלג אם aeroadmin-info.txt כבר קיים.
                await _aeroAdminSetup.RefreshAsync();
                await ReportCurrentInfoAsync();
            }
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
    /// tvinfo.ini (שנוסה תחילה) הוכח כמכיל רק מטא-דאטה של התקנה, לא ID/סיסמה -
    /// אלה קיימים רק בזיכרון התהליך ומוצגים על המסך לקריאה אנושית, אין קובץ
    /// לקרוא. במקום זה משתמשים בספריית UI-automation ייעודית
    /// (TeamViewer.QuickSupport.Integration, NuGet) שקוראת את הטקסט מתוך חלון
    /// ה-GUI. אזהרה: הספרייה הזו לא עודכנה מאז 2018 ובנויה ל-.NET Framework
    /// 4.5 - היא נבדקה שהיא נטענת (NuGet reference), אבל טרם אומתה בפועל מול
    /// הגרסה הנוכחית של QuickSupport. אם ה-Automator.GetInfo() זורק/נכשל,
    /// ייתכן שצריך להחליף אותה במימוש UI Automation עצמאי (System.Windows.Automation,
    /// כבר זמין תחת net8.0-windows) שקורא את אותם TextBox-ים ישירות.
    /// </summary>
    private async Task StartTeamViewerQuickSupportAsync()
    {
        if (!File.Exists(TeamViewerQsExe))
        {
            Logger.Warning("TeamViewerQS.exe not staged on this machine ({Path}) - install-teamviewer.ps1 may not have run", TeamViewerQsExe);
            return;
        }

        string? id = null;
        string? password = null;

        try
        {
            var automator = new TeamViewer.QuickSupport.Integration.Automator
            {
                AlternativePathToTeamViewer = TeamViewerQsExe,
            };
            // ריצה על thread נפרד: TestStack.White חוסם (סינכרוני) עד שהחלון מוכן
            // dynamic בכוונה - לא מאמת את שם המחלקה המדויק שמוחזר (לא מתועד
            // בבירור מעבר ל-"info.ID and info.Password" בדוגמת הספרייה)
            dynamic info = await Task.Run(() => (dynamic)automator.GetInfo());
            id = info?.ID;
            password = info?.Password;
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "TeamViewer.QuickSupport.Integration threw - library may be incompatible with the current QuickSupport UI, falling back to native UI Automation");
        }

        // נופל חזרה לקריאה ישירה מהחלון (System.Windows.Automation, כבר זמין
        // תחת net8.0-windows) אם הספרייה החיצונית נכשלה או החזירה ריק -
        // אותה גישה בדיוק כמו AeroAdminSetupService, כי אין שום ערובה שהספרייה
        // (לא עודכנה מ-2018) תואמת לגרסת QuickSupport הנוכחית.
        if (string.IsNullOrWhiteSpace(id) || string.IsNullOrWhiteSpace(password))
        {
            (id, password) = TryReadTeamViewerInfoNatively();
        }

        if (string.IsNullOrWhiteSpace(id) || string.IsNullOrWhiteSpace(password))
        {
            Logger.Warning("TeamViewer QuickSupport ID/password could not be read by either method");
            return;
        }

        if (_computerId == null) return;
        var path = $"computers/{_computerId}/remoteControl/teamviewer";
        var result = await _firebase.DbUpdateAsync(path, new Dictionary<string, object>
        {
            ["id"] = id,
            ["password"] = password,
            ["reportedAt"] = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(),
        });
        if (!result.Success)
        {
            Logger.Warning("TeamViewer QuickSupport info FAILED to report to Firebase: {Error}", result.Error);
            return;
        }
        Logger.Information("TeamViewer QuickSupport ID+password reported to Firebase for computer {ComputerId}", _computerId);
    }

    [DllImport("user32.dll")] private static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
    [DllImport("user32.dll")] private static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
    private delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    private static IntPtr FindTopLevelWindowForProcess(uint processId)
    {
        var found = IntPtr.Zero;
        EnumWindows((hWnd, _) =>
        {
            GetWindowThreadProcessId(hWnd, out var pid);
            if (pid == processId)
            {
                found = hWnd;
                return false;
            }
            return true;
        }, IntPtr.Zero);
        return found;
    }

    /// <summary>גיבוי ל-TeamViewer.QuickSupport.Integration (ראה הערה מעל
    /// StartTeamViewerQuickSupportAsync) - קורא ישירות מחלון ה-GUI של
    /// QuickSupport באמצעות System.Windows.Automation, אותה גישה בדיוק כמו
    /// AeroAdminSetupService. אזהרה: התבניות (regex) ל-ID/סיסמה כאן הן ניחוש
    /// סביר (ID: כ-9 ספרות, סיסמה: 4-6 ספרות) שלא אומת מול ה-UI האמיתי של
    /// QuickSupport - אם זה נכשל, ה-dump ב-teamviewer-ui-debug.txt נותן את
    /// הטקסטים האמיתיים בחלון כדי לתקן את התבניות בלי ניחוש נוסף.</summary>
    private (string? id, string? password) TryReadTeamViewerInfoNatively()
    {
        try
        {
            var process = Process.GetProcessesByName("TeamViewerQS").FirstOrDefault();
            if (process == null)
            {
                if (!File.Exists(TeamViewerQsExe)) return (null, null);
                process = Process.Start(new ProcessStartInfo(TeamViewerQsExe) { UseShellExecute = true });
                if (process == null) return (null, null);
                Thread.Sleep(3000); // זמן עלייה לפני שהחלון קיים
            }

            IntPtr handle;
            var deadline = DateTime.UtcNow + TimeSpan.FromSeconds(15);
            do
            {
                handle = FindTopLevelWindowForProcess((uint)process.Id);
                if (handle != IntPtr.Zero) break;
                Thread.Sleep(300);
            } while (DateTime.UtcNow < deadline);

            if (handle == IntPtr.Zero)
            {
                Logger.Warning("Native TeamViewer QuickSupport fallback: no top-level window found for process {Pid}", process.Id);
                return (null, null);
            }

            AutomationElement window;
            try { window = AutomationElement.FromHandle(handle); }
            catch { return (null, null); }

            var elements = window.FindAll(TreeScope.Descendants, Condition.TrueCondition);
            string? id = null, password = null;
            foreach (AutomationElement el in elements)
            {
                string value;
                try { value = el.Current.Name ?? string.Empty; }
                catch { continue; }
                if (string.IsNullOrWhiteSpace(value)) continue;

                if (id == null)
                {
                    var idMatch = Regex.Match(value, @"\b(\d[\d ]{7,10}\d)\b");
                    if (idMatch.Success) id = idMatch.Groups[1].Value.Replace(" ", "");
                }
                if (password == null && value.Trim() != id)
                {
                    var pwMatch = Regex.Match(value.Trim(), @"^\d{4,6}$");
                    if (pwMatch.Success) password = pwMatch.Value;
                }
            }

            if (id == null || password == null)
            {
                UiAutomationDebug.DumpTree(window, TeamViewerUiDebugFile, "TeamViewer QuickSupport - native fallback ID/password read");
            }

            return (id, password);
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "Native TeamViewer QuickSupport fallback threw");
            return (null, null);
        }
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
        _anyDeskIdRetryTimer?.Dispose();
        _aeroAdminSetupRetryTimer?.Dispose();
    }
}
