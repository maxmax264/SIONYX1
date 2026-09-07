using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text.RegularExpressions;
using System.Windows.Automation;
using Serilog;

namespace SionyxKiosk.Services;

/// <summary>
/// הגדרה של AeroAdmin (גיבוי רביעי, אחרי RustDesk/AnyDesk/TeamViewer).
///
/// גרסה מתוקנת: הניסיון הקודם ניווט בתפריט "Connection > Access rights" כדי
/// להגדיר סיסמת unattended-access קבועה - התפריט הזה מזוהה לפי שם באנגלית
/// ("Connection"/"Access rights"), אבל ב-screenshot בפועל מהקיוסק הממשק מותקן
/// עם תפריט מקומי (עברית) ושמות כאלה לא קיימים בכלל, כך שהאוטומציה נכשלה
/// תמיד ושום דבר לא נכתב ל-InfoFile - זו הסיבה ש-AeroAdmin רץ בפועל (עם
/// IP+PIN אמיתיים על המסך, כפי שאפשר לראות ב-screenshot) אבל לעולם לא דיווח
/// לדשבורד.
///
/// התיקון: אין צורך בתפריט הזה בכלל. מסך הבית של AeroAdmin (הפאנל השמאלי,
/// "לאפשר שליטה מרחוק") כבר מציג ישירות IP+PIN מוכנים לחיבור - קוראים אותם
/// ישירות מה-Text controls, בלי לנווט שום תפריט, כך שזה עובד בכל שפת ממשק.
/// ה-IP מזוהה כרצף הספרות הארוך (8+ ספרות, כמו RustDesk/AnyDesk ID), ה-PIN
/// כרצף קצר (4-6 ספרות) - שני ה-regex-ים האלה תלויים רק בתבנית הספרות עצמה,
/// לא בטקסט של תוויות השדות (שיכול להיות בכל שפה).
///
/// אזהרה: ה-PIN של AeroAdmin עלול להתחדש בכל הפעלה של האפליקציה (נפוץ בכלים
/// כאלה) - RefreshAsync (בניגוד ל-EnsureConfiguredAsync) קורא מחדש בכל פעם
/// בלי להסתמך על InfoFile קיים, כדי שכפתור "רענן" בדשבורד יביא ערך עדכני.
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
    private static readonly TimeSpan WindowTimeout = TimeSpan.FromSeconds(15);

    /// <summary>נקרא באתחול. לא עושה כלום אם כבר הוגדר פעם אחת בעבר
    /// (aeroadmin-info.txt קיים) או אם AeroAdmin לא מותקן - קריאה חד-פעמית
    /// זולה, בלי אוטומציית UI חדשה בכל עלייה של האפליקציה.</summary>
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

    /// <summary>נקרא מכפתור "רענן" בדשבורד - קורא מחדש את ה-IP/PIN הנוכחיים
    /// בלי להסתמך על InfoFile קיים, כי ה-PIN עלול להתחדש בכל הפעלה של
    /// AeroAdmin ואת זה EnsureConfiguredAsync לא יתפוס (מדלג אם הקובץ קיים).</summary>
    public async Task RefreshAsync()
    {
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
            // אם AeroAdmin כבר רץ ברקע (מהפעלה קודמת - ראו ה-finally, לא סוגרים
            // אותו אף פעם) - משתמשים בתהליך הקיים במקום לפתוח עותק כפול.
            process = Process.GetProcessesByName("AeroAdmin").FirstOrDefault();
            var startedNewProcess = false;
            if (process == null)
            {
                var psi = new ProcessStartInfo(ExePath)
                {
                    UseShellExecute = true,
                    WindowStyle = ProcessWindowStyle.Hidden,
                };
                process = Process.Start(psi);
                startedNewProcess = true;
            }

            if (process == null)
            {
                Logger.Warning("Failed to start AeroAdmin.exe");
                return;
            }

            var mainWindow = WaitForMainWindow(process);
            if (mainWindow == null)
            {
                Logger.Warning("AeroAdmin main window did not appear within {Timeout}s - cannot read IP/PIN", WindowTimeout.TotalSeconds);
                return;
            }

            var id = ReadOwnId(mainWindow);
            if (string.IsNullOrWhiteSpace(id))
            {
                Logger.Warning("Could not read AeroAdmin's own IP/ID from the main window - see class comment");
                UiAutomationDebug.DumpTree(mainWindow, UiDebugFile, "AeroAdmin - reading own IP/ID");
                return;
            }

            var pin = ReadOwnPin(mainWindow, id);
            if (string.IsNullOrWhiteSpace(pin))
            {
                Logger.Warning("Could not read AeroAdmin's own PIN from the main window - see class comment");
                UiAutomationDebug.DumpTree(mainWindow, UiDebugFile, "AeroAdmin - reading own PIN");
                return;
            }

            File.WriteAllText(InfoFile,
                $"AeroAdmin ID: {id}\r\nAeroAdmin Password: {pin}\r\n");
            Logger.Information("AeroAdmin info (re-)written to {Path} (process was {NewOrExisting})",
                InfoFile, startedNewProcess ? "newly started" : "already running");
        }
        catch (Exception ex)
        {
            Logger.Error(ex, "AeroAdmin setup/refresh failed");
        }
        finally
        {
            // משאירים את AeroAdmin רץ ברקע (מוסתר) - זה מה שמאפשר חיבור unattended
            // מבחוץ; לא סוגרים את התהליך כאן, גם אם פתחנו אותו כרגע.
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

    private static string? ReadOwnId(AutomationElement mainWindow)
    {
        // ה-IP/ID העצמי מוצג כטקסט בחלון הבית, בפורמט קבוצות ספרות (למשל
        // "832 796 561"). מחפשים בין כל ה-Text controls את הראשון שמתאים
        // לתבנית של רצף ספרות ארוך (8+) - זה עובד בכל שפת ממשק, כי לא
        // מסתמכים על טקסט התווית ("IP" וכו'), רק על תבנית הספרות.
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

    /// <summary>ה-PIN מוצג כרצף ספרות קצר (4-6 ספרות) - נבדל מה-ID (8+ ספרות)
    /// בגלל האורך, לא בגלל טקסט תווית כלשהו, אז זה עובד גם בממשק מקומי
    /// (עברית וכו').</summary>
    private static string? ReadOwnPin(AutomationElement mainWindow, string excludeId)
    {
        var texts = mainWindow.FindAll(TreeScope.Descendants,
            new PropertyCondition(AutomationElement.ControlTypeProperty, ControlType.Text));
        foreach (AutomationElement text in texts)
        {
            var value = text.Current.Name?.Trim();
            if (string.IsNullOrWhiteSpace(value)) continue;
            if (!Regex.IsMatch(value, @"^\d{4,6}$")) continue;
            if (value == excludeId) continue;
            return value;
        }
        return null;
    }
}
