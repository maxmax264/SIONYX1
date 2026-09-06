using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;
using System.Text.RegularExpressions;
using System.Windows.Automation;
using Serilog;

namespace SionyxKiosk.Services;

/// <summary>
/// הגדרה חד-פעמית של AeroAdmin (גיבוי רביעי, אחרי RustDesk/AnyDesk/TeamViewer).
///
/// אזהרה חשובה - בניגוד לשלושת הכלים האחרים, לAeroAdmin אין שום CLI/קובץ-קונפיג
/// קריא: אין דגל /silent, ואין דרך להזין/לקרוא סיסמה חוץ מדיאלוג ה-GUI שלו
/// (מתועד ב-aeroadmin.com/en/unattended_access.html, לא ניחוש). המימוש כאן:
///   1. מפעיל את AeroAdmin.exe עם חלון מוסתר (WindowStyle=Hidden) כדי שלא
///      יוצג ללקוח בקופה.
///   2. עם System.Windows.Automation (זמין תחת net8.0-windows, לא דורש NuGet
///      נוסף) פותח את Connection > Access rights, מוסיף ID="ANY" עם סיסמה
///      אקראית, ואז קורא את ה-ID העצמי של המכונה מחלון הבית.
///   3. כותב את שניהם ל-aeroadmin-info.txt באותו פורמט של הכלים האחרים, כדי
///      ש-RemoteControlReportingService (שכבר "מחכה" לקובץ הזה) ידווח אותו
///      ל-Firebase בלי שינוי.
///
/// ה-AutomationId/Name המדויקים של הכפתורים והתפריטים בקוד הזה *לא אומתו* מול
/// האפליקציה האמיתית - אין לי דרך להריץ Windows GUI ולבדוק. לפני שסומכים על
/// זה: להריץ פעם אחת עם Logger.Debug מודלק, לפתוח את AeroAdmin.exe הרגיל לצד
/// זה, ולהשתמש ב-Accessibility Insights for Windows (כלי חינמי של מיקרוסופט)
/// כדי לראות את שמות ה-AutomationId/Name האמיתיים ולעדכן את הקבועים למטה.
/// </summary>
public class AeroAdminSetupService
{
    private static readonly ILogger Logger = Log.ForContext<AeroAdminSetupService>();

    // public: RemoteControlReportingService uses this to self-heal (re-run
    // install-aeroadmin.ps1 if the exe is missing, e.g. on a kiosk that was
    // installed before this feature existed and only ever got an in-place
    // app update, not a full reinstall).
    public const string ExePath = @"C:\ProgramData\SIONYX\AeroAdmin.exe";
    private const string InfoFile = @"C:\ProgramData\SIONYX\aeroadmin-info.txt";
    private const string UiDebugFile = @"C:\ProgramData\SIONYX\aeroadmin-ui-debug.txt";

    // TODO: לאמת מול האפליקציה האמיתית עם Accessibility Insights ולעדכן -
    // אלה ניחושים סבירים בהתבסס על screenshots רשמיים, לא ערכים מאומתים.
    private const string ConnectionMenuName = "Connection";
    private const string AccessRightsMenuItemName = "Access rights";
    private const string AddButtonName = "+";
    private const string OkButtonName = "OK";
    private static readonly TimeSpan WindowTimeout = TimeSpan.FromSeconds(15);

    /// <summary>נקרא באתחול ובכל refresh מהדשבורד. לא עושה כלום אם כבר הוגדר
    /// פעם אחת בעבר (aeroadmin-info.txt קיים) או אם AeroAdmin לא מותקן.</summary>
    public async Task EnsureConfiguredAsync()
    {
        if (File.Exists(InfoFile))
        {
            Logger.Debug("AeroAdmin already configured previously ({Path}) - skipping", InfoFile);
            return;
        }

        if (!File.Exists(ExePath))
        {
            Logger.Debug("AeroAdmin.exe not staged yet - install-aeroadmin.ps1 may not have run");
            return;
        }

        await Task.Run(RunSetup);
    }

    private void RunSetup()
    {
        Process? process = null;
        try
        {
            var psi = new ProcessStartInfo(ExePath)
            {
                UseShellExecute = true,
                WindowStyle = ProcessWindowStyle.Hidden,
            };
            process = Process.Start(psi);
            if (process == null)
            {
                Logger.Warning("Failed to start AeroAdmin.exe");
                return;
            }

            var mainWindow = WaitForMainWindow(process);
            if (mainWindow == null)
            {
                Logger.Warning("AeroAdmin main window did not appear within {Timeout}s - cannot read ID/set password", WindowTimeout.TotalSeconds);
                return;
            }

            var password = GenerateRandomPassword(16);
            var configured = TryAddAccessRight(mainWindow, password);
            if (!configured)
            {
                Logger.Warning("Could not automate Connection > Access rights - AutomationId/Name constants in AeroAdminSetupService.cs likely need updating against the real UI (see class comment)");
                UiAutomationDebug.DumpTree(mainWindow, UiDebugFile, "AeroAdmin - Connection > Access rights automation");
                return;
            }

            var id = ReadOwnId(mainWindow);
            if (string.IsNullOrWhiteSpace(id))
            {
                Logger.Warning("Could not read AeroAdmin's own ID from the main window - see class comment");
                UiAutomationDebug.DumpTree(mainWindow, UiDebugFile, "AeroAdmin - reading own ID");
                return;
            }

            File.WriteAllText(InfoFile,
                $"AeroAdmin ID: {id}\r\nAeroAdmin Password: {password}\r\n");
            Logger.Information("AeroAdmin configured for the first time and info written to {Path}", InfoFile);
        }
        catch (Exception ex)
        {
            Logger.Error(ex, "AeroAdmin one-time setup failed");
        }
        finally
        {
            // משאירים את AeroAdmin רץ ברקע (מוסתר) - זה מה שמאפשר חיבור unattended
            // מבחוץ; לא סוגרים את התהליך כאן.
            process?.Dispose();
        }
    }

    [DllImport("user32.dll")] private static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
    [DllImport("user32.dll")] private static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
    private delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    /// <summary>Process.MainWindowHandle מסנן במפורש רק חלונות *גלויים* - אצלנו
    /// החלון מוסתר בכוונה (WindowStyle=Hidden), אז הוא לעולם לא יוחזר משם. צריך
    /// EnumWindows גולמי שמסנן רק לפי process id, בלי תלות בנראות.</summary>
    private static AutomationElement? WaitForMainWindow(Process process)
    {
        var deadline = DateTime.UtcNow + WindowTimeout;
        while (DateTime.UtcNow < deadline)
        {
            var handle = FindTopLevelWindowForProcess((uint)process.Id);
            if (handle != IntPtr.Zero)
            {
                try { return AutomationElement.FromHandle(handle); }
                catch { /* חלון עוד לא מוכן לגמרי - ננסה שוב */ }
            }
            Thread.Sleep(300);
        }
        return null;
    }

    private static IntPtr FindTopLevelWindowForProcess(uint processId)
    {
        var found = IntPtr.Zero;
        EnumWindows((hWnd, _) =>
        {
            GetWindowThreadProcessId(hWnd, out var pid);
            if (pid == processId)
            {
                found = hWnd;
                return false; // מספיק חלון אחד - עוצר את החיפוש
            }
            return true;
        }, IntPtr.Zero);
        return found;
    }

    private static bool TryAddAccessRight(AutomationElement mainWindow, string password)
    {
        // Connection > Access rights
        var connectionMenu = FindByNameAnyType(mainWindow, ConnectionMenuName);
        if (connectionMenu == null) return false;
        Invoke(connectionMenu);

        var accessRightsItem = FindByNameAnyType(mainWindow, AccessRightsMenuItemName, TreeScope.Descendants);
        if (accessRightsItem == null) return false;
        Invoke(accessRightsItem);

        // הדיאלוג נפתח כחלון נפרד (top-level) - מחפשים אותו מחדש מתחת ל-Desktop
        var dialog = WaitForChildWindow(AccessRightsMenuItemName, TimeSpan.FromSeconds(5));
        if (dialog == null) return false;

        var addButton = FindByNameAnyType(dialog, AddButtonName);
        if (addButton == null) return false;
        Invoke(addButton);

        // שדות הטופס - "ANY" ל-ID, שם, וסיסמה פעמיים (אימות). מזוהים לפי סדר
        // כי אין לנו AutomationId מאומת; אם הסדר שונה בפועל, זה המקום לתקן.
        var editFields = dialog.FindAll(TreeScope.Descendants,
            new PropertyCondition(AutomationElement.ControlTypeProperty, ControlType.Edit));
        if (editFields.Count < 3) return false;

        SetText(editFields[0], "ANY");
        SetText(editFields[1], "SIONYX Kiosk");
        SetText(editFields[2], password);
        if (editFields.Count >= 4) SetText(editFields[3], password); // אימות סיסמה, אם קיים

        var okButton = FindByNameAnyType(dialog, OkButtonName);
        if (okButton == null) return false;
        Invoke(okButton);

        return true;
    }

    private static string? ReadOwnId(AutomationElement mainWindow)
    {
        // ה-ID העצמי מוצג כטקסט בחלון הבית, בפורמט קבוצות ספרות (למשל
        // "123 456 789"). מחפשים בין כל ה-Text controls את הראשון שמתאים
        // לתבנית הזו.
        var texts = mainWindow.FindAll(TreeScope.Descendants,
            new PropertyCondition(AutomationElement.ControlTypeProperty, ControlType.Text));
        foreach (AutomationElement text in texts)
        {
            var value = text.Current.Name;
            if (string.IsNullOrWhiteSpace(value)) continue;
            var match = Regex.Match(value, @"(\d[\d \-]{7,})");
            if (match.Success)
            {
                return match.Groups[1].Value.Replace(" ", "").Replace("-", "");
            }
        }
        return null;
    }

    private static AutomationElement? FindByNameAnyType(AutomationElement root, string name, TreeScope scope = TreeScope.Children)
    {
        return root.FindFirst(scope, new PropertyCondition(AutomationElement.NameProperty, name));
    }

    private static AutomationElement? WaitForChildWindow(string nameContains, TimeSpan timeout)
    {
        var deadline = DateTime.UtcNow + timeout;
        while (DateTime.UtcNow < deadline)
        {
            var desktop = AutomationElement.RootElement;
            var windows = desktop.FindAll(TreeScope.Children,
                new PropertyCondition(AutomationElement.ControlTypeProperty, ControlType.Window));
            foreach (AutomationElement window in windows)
            {
                if (window.Current.Name?.Contains(nameContains, StringComparison.OrdinalIgnoreCase) == true)
                    return window;
            }
            Thread.Sleep(200);
        }
        return null;
    }

    private static void Invoke(AutomationElement element)
    {
        if (element.TryGetCurrentPattern(InvokePattern.Pattern, out var pattern))
        {
            ((InvokePattern)pattern).Invoke();
        }
    }

    private static void SetText(AutomationElement element, string value)
    {
        if (element.TryGetCurrentPattern(ValuePattern.Pattern, out var pattern))
        {
            ((ValuePattern)pattern).SetValue(value);
        }
    }

    private static string GenerateRandomPassword(int length)
    {
        const string chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
        var bytes = System.Security.Cryptography.RandomNumberGenerator.GetBytes(length);
        var result = new char[length];
        for (int i = 0; i < length; i++) result[i] = chars[bytes[i] % chars.Length];
        return new string(result);
    }
}
