using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
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
///
/// ממצא חדש וחשוב (אחרי בדיקה מול התיעוד הרשמי של AeroAdmin): ה-ID+PIN
/// שמוצגים במסך הבית (ומדווחים כרגע לדשבורד) הם קוד חיבור *חד-פעמי* בלבד -
/// לפי AeroAdmin, חיבור איתם מציג בקשת אישור מקומית (accept/reject) בצד
/// המחשב המרוחק. בקיוסק בלי אף אחד מול המסך זה אומר שחיבור עם הפרטים
/// שהדשבורד מציג היום עלול פשוט להיתקע מחכה לאישור שלעולם לא יגיע. כדי
/// לקבל unattended access אמיתי (בלי אישור ידני) צריך להגדיר סיסמה קבועה
/// דרך "Connection > Access rights" בתפריט - זה בדיוק מה שהניסיון הקודם
/// ניסה לעשות וכשל כי הוא הניח טקסט תפריט אנגלי קבוע על התקנה בעברית.
/// DumpMenuStructureOnce (למטה) הוא צעד ראשון בטוח (בלי ללחוץ בתוך אף תפריט)
/// לתעד את השמות/מבנה האמיתיים בשפה המותקנת בפועל, כדי שהאוטומציה הבאה של
/// "Access rights" תיבנה נגד המחרוזות שבאמת קיימות ולא תנחש שוב.
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
    private const string MenuDebugFile = @"C:\ProgramData\SIONYX\aeroadmin-menu-debug.txt";
    private const string ConnectDialogDebugFile = @"C:\ProgramData\SIONYX\aeroadmin-connect-dialog-debug.txt";
    private static readonly TimeSpan WindowTimeout = TimeSpan.FromSeconds(15);

    // 08/09: נשמר בזמן RunSetup כדי ש-WatchForConnectionDialogOnce (מטה) ידע
    // להבדיל בין "החלון הראשי הרגיל" (מותר, מוכר) לבין "חלון חדש שקפץ" (חשוד
    // כבקשת אישור חיבור נכנס) - בלי זה כל בדיקה הייתה חושבת שהחלון הראשי עצמו
    // הוא בקשת חיבור.
    private static IntPtr _knownMainWindowHandle = IntPtr.Zero;

    /// <summary>נקרא באתחול. לא עושה כלום אם כבר הוגדר פעם אחת בעבר
    /// (aeroadmin-info.txt קיים) או אם AeroAdmin לא מותקן - קריאה חד-פעמית
    /// זולה, בלי אוטומציית UI חדשה בכל עלייה של האפליקציה.</summary>
    /// <summary>
    /// תוקן (09/09, באג אמיתי שנמצא בשטח): EnsureConfiguredAsync מדלג לגמרי
    /// ברגע ש-InfoFile קיים - המקרה הרגיל בקיוסק שכבר רץ מתמיד, כי AeroAdmin
    /// כבר הוגדר בעבר ונשאר חי. הבעיה: _knownMainWindowHandle מוגדר *רק*
    /// בתוך RunSetup, שאף פעם לא רץ במקרה הזה - כלומר QuickCheckForPinChange
    /// (שבודק `if (_knownMainWindowHandle == IntPtr.Zero) return null`) נשאר
    /// no-op *לכל אורך חיי האפליקציה* על קיוסק שלא הופעל מחדש, גם אם AeroAdmin
    /// עצמו רץ בסדר גמור ו-PIN שלו משתנה כל הזמן על המסך. נקרא תמיד באתחול,
    /// בלי תלות ב-EnsureConfiguredAsync, כדי לתפוס את ה-handle של החלון הקיים.
    /// </summary>
    public void AttachToRunningWindowIfAny()
    {
        try
        {
            var process = Process.GetProcessesByName("AeroAdmin").FirstOrDefault();
            if (process == null) return; // אין תהליך רץ - EnsureHidden/EnsureConfiguredAsync יטפלו

            var mainWindow = WaitForMainWindow(process);
            if (mainWindow == null)
            {
                Logger.Debug("AttachToRunningWindowIfAny: AeroAdmin process exists but main window not found");
                return;
            }
            _knownMainWindowHandle = new IntPtr(mainWindow.Current.NativeWindowHandle);
            Logger.Information("AttachToRunningWindowIfAny: attached to existing AeroAdmin window (handle known - QuickCheckForPinChange can work now)");
        }
        catch (Exception ex)
        {
            Logger.Debug(ex, "AttachToRunningWindowIfAny failed (non-fatal)");
        }
    }

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

    private static Process? StartHiddenProcess()
    {
        // הערה חשובה (08/09, אומת בשטח): WindowStyle=Hidden כאן הוא רק
        // "רמז" ל-CreateProcess (nCmdShow=SW_HIDE) - הרבה אפליקציות
        // Win32 (וגם AeroAdmin, כנראה) מתעלמות ממנו וקוראות בעצמן
        // ShowWindow(SW_SHOW) בהפעלה, ולכן החלון קפץ בפועל וקטע את
        // סשן הקיוסק. במקום לסמוך על הרמז, מכריחים הסתרה עם
        // ShowWindow/SW_HIDE אמיתי ברגע שהחלון נמצא, ראו HideAllWindowsForProcess.
        var psi = new ProcessStartInfo(ExePath)
        {
            UseShellExecute = true,
            WindowStyle = ProcessWindowStyle.Hidden,
        };
        return Process.Start(psi);
    }

    /// <summary>
    /// בדיקה קלה ומהירה (בלי להפעיל/להסתיר תהליך, בלי RunSetup מלא) - נועדה
    /// לרוץ בתדירות גבוהה (כל כמה שניות) כדי לתפוס שינוי PIN כמעט מיידית.
    /// PIN מתחלף בכל דחיית חיבור/timeout, וטיימר של 5 דקות (RetryAeroAdminSetup)
    /// גורם לדשבורד להראות פרטים ישנים במשך עד 5 דקות בכל פעם. מחזיר את
    /// ה-ID+PIN הנוכחיים אם הצליח לקרוא ואם הם שונים מהערך שכבר ב-InfoFile,
    /// null אם אין שינוי או שהקריאה נכשלה (למשל החלון עוד לא מוכן/נסגר -
    /// לא בעיה, ה-tick הבא ינסה שוב).
    /// </summary>
    public string? QuickCheckForPinChange()
    {
        if (_knownMainWindowHandle == IntPtr.Zero)
        {
            // תוקן (09/09): במקום לוותר לצמיתות, מנסים להתחבר לחלון קיים -
            // מכסה כל מקרה שבו AttachToRunningWindowIfAny לא הצליח באתחול
            // (למשל AeroAdmin עוד לא סיים לעלות באותו רגע).
            AttachToRunningWindowIfAny();
            if (_knownMainWindowHandle == IntPtr.Zero) return null;
        }
        try
        {
            AutomationElement mainWindow;
            try { mainWindow = AutomationElement.FromHandle(_knownMainWindowHandle); }
            catch { return null; } // החלון נסגר/התהליך מת - EnsureHidden יטפל בהפעלה מחדש

            var id = ReadOwnId(mainWindow);
            if (string.IsNullOrWhiteSpace(id)) return null;
            var pin = ReadOwnPin(mainWindow, id);
            if (string.IsNullOrWhiteSpace(pin)) return null;

            var current = $"AeroAdmin ID: {id}\r\nAeroAdmin Password: {pin}\r\n";
            if (File.Exists(InfoFile) && File.ReadAllText(InfoFile) == current) return null; // אין שינוי

            File.WriteAllText(InfoFile, current);
            Logger.Information("AeroAdmin PIN changed - updated {Path} immediately (ID {Id})", InfoFile, id);
            return current;
        }
        catch (Exception ex)
        {
            Logger.Debug(ex, "QuickCheckForPinChange failed (non-fatal, next tick will retry)");
            return null;
        }
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
                process = StartHiddenProcess();
                startedNewProcess = true;
            }

            if (process == null)
            {
                Logger.Warning("Failed to start AeroAdmin.exe");
                return;
            }

            // מכריחים הסתרה אמיתית מיד - גם אם AeroAdmin כבר פתח לעצמו חלון
            // גלוי (למשל דיאלוג רישוי/EULA בהפעלה ראשונה) לפני שהגענו לכאן.
            HideAllWindowsForProcess((uint)process.Id);

            var mainWindow = WaitForMainWindow(process);
            if (mainWindow == null)
            {
                Logger.Warning("AeroAdmin main window did not appear within {Timeout}s - cannot read IP/PIN", WindowTimeout.TotalSeconds);
                return;
            }

            // רושמים את ה-handle כ"מוכר" כדי ש-WatchForConnectionDialogOnce לא
            // יתבלבל ויחשוב שהחלון הראשי הרגיל הוא בקשת חיבור נכנס.
            _knownMainWindowHandle = new IntPtr(mainWindow.Current.NativeWindowHandle);

            // מסתירים שוב אחרי שנמצא (יכול להיות שהופיע רק עכשיו, או שהמסך
            // הקודם היה חלון אחר של אותו תהליך).
            HideAllWindowsForProcess((uint)process.Id);

            // אבחון חד-פעמי, בלי תופעות לוואי: פותח (רק פותח, אף פעם לא לוחץ
            // פנימה) כל תפריט עליון כדי לתעד את שמות הפריטים האמיתיים בשפה
            // המותקנת בפועל. זה קיים כי ה"תיקון" הקודם (ניווט "Connection >
            // Access rights") הניח טקסט אנגלי קבוע וזה כשל בשקט על ממשק מקומי -
            // הדאמפ הזה ייתן לנו את המחרוזות/מבנה האמיתיים כדי לבנות אוטומציה
            // מדויקת בפעם הבאה, במקום לנחש שוב.
            DumpMenuStructureOnce(mainWindow);

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
            // מבחוץ; לא סוגרים את התהליך כאן, גם אם פתחנו אותו כרגע. מסתירים
            // שוב פעם אחרונה ליתר ביטחון (למשל אם קריאת ה-ID/PIN גרמה לחלון
            // חדש/דיאלוג לצוץ) לפני שמשחררים את המשתנה.
            if (process != null)
            {
                try { HideAllWindowsForProcess((uint)process.Id); }
                catch { /* לא קריטי - הטיימר התקופתי ב-EnsureHidden ינסה שוב */ }
            }
            process?.Dispose();
        }
    }

    /// <summary>נקרא באופן תקופתי (טיימר קצר, בלתי תלוי בהגדרה חד-פעמית) כדי
    /// להבטיח ש-AeroAdmin לעולם לא נשאר גלוי מול הקופאי - בניגוד ל-
    /// EnsureConfiguredAsync/RefreshAsync, זה תמיד רץ, גם אחרי שההגדרה כבר
    /// הצליחה פעם אחת, כי החלון עלול לקפוץ שוב מכל סיבה (קליק בטעות, דיאלוג
    /// עדכון של AeroAdmin עצמו וכו').</summary>
    /// <summary>
    /// רץ ללא תלות ב-EnsureConfiguredAsync/InfoFile - זה קריטי, כי
    /// EnsureConfiguredAsync מדלג לגמרי ברגע ש-aeroadmin-info.txt קיים, בלי
    /// לבדוק אם התהליך בפועל עדיין חי. תוקן (08/09, נמצא בשטח): בלי זה,
    /// ברגע ש-AeroAdmin נסגר/קורס מכל סיבה (restart של הקיוסק, לדוגמה) אחרי
    /// שכבר נקרא פעם אחת ה-ID/PIN - שום דבר לא מפעיל אותו מחדש לנצח, והדשבורד
    /// ממשיך להראות פרטים ישנים בזמן שהקיוסק בפועל "לא מקוון" (offline) מבחינת
    /// שרתי AeroAdmin. עכשיו: אם התהליך לא רץ - מפעילים אותו מחדש ומסתירים.
    /// </summary>
    /// <summary>
    /// רץ ללא תלות ב-EnsureConfiguredAsync/InfoFile - זה קריטי, כי
    /// EnsureConfiguredAsync מדלג לגמרי ברגע ש-aeroadmin-info.txt קיים, בלי
    /// לבדוק אם התהליך בפועל עדיין חי. תוקן (08/09, נמצא בשטח): בלי זה,
    /// ברגע ש-AeroAdmin נסגר/קורס מכל סיבה (restart של הקיוסק, לדוגמה) אחרי
    /// שכבר נקרא פעם אחת ה-ID/PIN - שום דבר לא מפעיל אותו מחדש לנצח, והדשבורד
    /// ממשיך להראות פרטים ישנים בזמן שהקיוסק בפועל "לא מקוון" (offline) מבחינת
    /// שרתי AeroAdmin. עכשיו: אם התהליך לא רץ - מפעילים אותו מחדש ומסתירים.
    /// מחזיר true אם בוצע הפעלה מחדש בפועל - הקורא (RemoteControlReportingService)
    /// צריך במקרה כזה לקרוא ל-RefreshAsync, כי ID/PIN חדשים נוצרים בכל הפעלה
    /// מחדש של התהליך והדשבורד חייב להתעדכן, לא רק "שהתהליך חי".
    /// </summary>
    public bool EnsureHidden()
    {
        try
        {
            var process = Process.GetProcessesByName("AeroAdmin").FirstOrDefault();
            var restarted = false;
            if (process == null)
            {
                process = StartHiddenProcess();
                if (process == null)
                {
                    Logger.Warning("EnsureHidden: AeroAdmin was not running and failed to restart it");
                    return false;
                }
                restarted = true;
                Logger.Information("EnsureHidden: AeroAdmin process was gone - restarted it (pid {Pid})", process.Id);
            }
            HideAllWindowsForProcess((uint)process.Id);
            return restarted;
        }
        catch (Exception ex)
        {
            Logger.Debug(ex, "EnsureHidden failed (non-fatal, will retry next tick)");
            return false;
        }
    }

    /// <summary>
    /// אבחון חד-פעמי ובטוח (בלי שום לחיצה), אותו רעיון בדיוק כמו
    /// DumpMenuStructureOnce: מחפש כל חלון עליון של תהליך AeroAdmin שהוא
    /// *לא* החלון הראשי הידוע (_knownMainWindowHandle) - חלון כזה כנראה
    /// דיאלוג בקשת חיבור נכנס ("מישהו רוצה להתחבר, לאשר?") - ומתעד את המבנה
    /// שלו כדי שנוכל לבנות אחר כך לחיצה אוטומטית אמיתית (InvokePattern) נגד
    /// השמות האמיתיים, בלי לנחש. מוגן ע"י קיום הקובץ עצמו - לא רץ שוב אחרי
    /// שכבר תיעד פעם אחת.
    ///
    /// למה זה חשוב: המשתמש דיווח שכל ניסיון חיבור מחדש ל-PIN הנוכחי (בקוד
    /// חד-פעמי) גם מחדש את ה-PIN, כך שאי אפשר סתם "לנסות שוב" בלי לתעד קודם.
    /// ברגע שיהיה לנו דאמפ אמיתי, בונים כאן Invoke על כפתור האישור במקום
    /// לנווט לתפריט "Access rights" שהתברר כבלתי-נגיש ל-UI Automation בכלל.
    /// </summary>
    public void WatchForConnectionDialogOnce()
    {
        if (File.Exists(ConnectDialogDebugFile)) return;
        if (_knownMainWindowHandle == IntPtr.Zero) return; // עוד לא הוגדר החלון הראשי - אין מה להשוות אליו

        try
        {
            var process = Process.GetProcessesByName("AeroAdmin").FirstOrDefault();
            if (process == null) return;

            var candidate = IntPtr.Zero;
            EnumWindows((hWnd, _) =>
            {
                GetWindowThreadProcessId(hWnd, out var pid);
                if (pid == (uint)process.Id && hWnd != _knownMainWindowHandle)
                {
                    candidate = hWnd;
                    return false;
                }
                return true;
            }, IntPtr.Zero);

            if (candidate == IntPtr.Zero) return; // אין כרגע שום חלון חדש - זה תקין, רוב הזמן

            AutomationElement? element;
            try { element = AutomationElement.FromHandle(candidate); }
            catch { return; }
            if (element == null) return;

            UiAutomationDebug.DumpTree(element, ConnectDialogDebugFile, "AeroAdmin - unexpected extra window (possibly incoming-connection prompt)");
            Logger.Information("AeroAdmin showed an extra window beyond the main one - dumped to {Path} for building auto-approve automation", ConnectDialogDebugFile);
        }
        catch (Exception ex)
        {
            Logger.Debug(ex, "WatchForConnectionDialogOnce failed (non-fatal, one-time diagnostic only)");
        }
    }

    private const int SW_SHOWNOACTIVATE = 4;
    private const uint SWP_NOSIZE = 0x0001;
    private const uint SWP_NOZORDER = 0x0004;
    private const uint SWP_NOACTIVATE = 0x0010;
    // הרבה מחוץ לכל שטח מסך אפשרי (גם multi-monitor) - שם החלון "קיים וגלוי"
    // מבחינת Windows אבל אף אחד לא רואה אותו בפועל.
    private const int OffscreenX = -32000;
    private const int OffscreenY = -32000;

    [DllImport("user32.dll")] private static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] private static extern bool SetWindowPos(
        IntPtr hWnd, IntPtr hWndInsertAfter, int x, int y, int cx, int cy, uint flags);

    /// <summary>
    /// מזיז בכוח (לא מסתיר!) את *כל* החלונות העליונים של התהליך הרחק מחוץ
    /// לשטח המסך - לא רק ה"חלון הראשי" - כי דיאלוג EULA/רישוי בהפעלה ראשונה
    /// או חלון משנה יכולים להיות תהליך-ID תואם אבל handle שונה מזה שנמצא
    /// לצורך קריאת ה-ID/PIN.
    ///
    /// תוקן (09/09, באג אמיתי שנמצא בשטח): בהתחלה זה עשה ShowWindow(SW_HIDE)
    /// אמיתי - אבל אז הדשבורד המשיך להראות PIN ישן לצמיתות גם אחרי שהמשתמש
    /// אימת שה-PIN האמיתי על המסך כן השתנה, ו-QuickCheckForPinChange (שרץ
    /// כל 3 שניות ומאושר בלוג שהוא רץ) פשוט ממשיך לקרוא את הערך הישן. ההשערה:
    /// AeroAdmin (כמו הרבה אפליקציות GUI) מפסיק לרענן את הטקסט הפנימי שלו
    /// (ה-PIN בפרט, שמתחדש עצמאית ע"י התוכנה) כשהחלון שלו מוסתר (SW_HIDE),
    /// כי הוא בודק IsWindowVisible/מדלג על ציור בחלון נסתר לחיסכון במשאבים -
    /// כך שהערך הפנימי שה-UI Automation קורא נשאר קפוא על הערך מרגע ההסתרה
    /// ולא באמת מתעדכן, גם אם ברמת הפרוטוקול/רשת ה-PIN כבר התחלף.
    /// הפתרון: להזיז את החלון מחוץ לגבולות המסך במקום להסתיר אותו - מבחינת
    /// Windows/IsWindowVisible הוא עדיין "מוצג כרגיל" (SW_SHOWNOACTIVATE, לא
    /// SW_HIDE) אז האפליקציה ממשיכה לצייר/לרענן את עצמה כרגיל ברקע, בלי
    /// שהקופאי יראה אותו בפועל כי הוא פיזית מחוץ לכל מסך.
    /// </summary>
    private static void HideAllWindowsForProcess(uint processId)
    {
        EnumWindows((hWnd, _) =>
        {
            GetWindowThreadProcessId(hWnd, out var pid);
            if (pid == processId)
            {
                ShowWindow(hWnd, SW_SHOWNOACTIVATE);
                SetWindowPos(hWnd, IntPtr.Zero, OffscreenX, OffscreenY, 0, 0,
                    SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE);
            }
            return true; // ממשיכים לכל החלונות, לא עוצרים בראשון
        }, IntPtr.Zero);
    }

    /// <summary>
    /// אבחון חד-פעמי (מוגן ע"י קיום הקובץ עצמו - לא רץ שוב אחרי הפעם
    /// הראשונה): פותח כל תפריט עליון כדי לתעד את שמות/AutomationId של
    /// הפריטים, בלי ללחוץ לתוך אף פריט - אין כאן שום סיכון להפעיל פעולה לא
    /// רצויה (יציאה, הסרת התקנה וכו').
    ///
    /// למה זה קיים: כדי להשיג unattended access אמיתי (בלי אישור ידני מקומי
    /// בכל חיבור) ב-AeroAdmin צריך לנווט "Connection > Access rights" ולהוסיף
    /// סיסמה קבועה - ה-PIN שמוצג במסך הבית (מה ש-ReadOwnPin קורא) הוא רק קוד
    /// חיבור חד-פעמי, ולפי התיעוד הרשמי של AeroAdmin חיבור באמצעותו מציג
    /// בקשת אישור מקומית (accept/reject) - בקיוסק בלי אף אחד מול המסך, זה
    /// אומר שחיבור בפועל עם ה-ID+PIN שכבר מדווחים לדשבורד עלול פשוט להיתקע
    /// מחכה לאישור שאף אחד לא ילחץ עליו. הניסיון הקודם לנווט את התפריט הזה
    /// הניח טקסט אנגלי קבוע ("Connection"/"Access rights") וכשל בשקט על
    /// התקנה עם ממשק מקומי (עברית) - הדאמפ הזה קודם כל מתעד את השמות/מבנה
    /// האמיתיים כדי שהאוטומציה הבאה תיבנה נגד המחרוזות שבאמת מוצגות, במקום
    /// לנחש שוב.
    /// </summary>
    private static void DumpMenuStructureOnce(AutomationElement mainWindow)
    {
        if (File.Exists(MenuDebugFile)) return;

        try
        {
            var sb = new StringBuilder();
            sb.AppendLine($"AeroAdmin menu dump - {DateTime.Now}");

            var menuBar = mainWindow.FindFirst(TreeScope.Descendants,
                new PropertyCondition(AutomationElement.ControlTypeProperty, ControlType.MenuBar));
            if (menuBar == null)
            {
                sb.AppendLine("No MenuBar element found in the UI tree (classic Win32 menu may not expose via UIA - see full tree in " + UiDebugFile + ").");
                UiAutomationDebug.DumpTree(mainWindow, UiDebugFile, "AeroAdmin - no MenuBar found, full tree for manual inspection");
                File.WriteAllText(MenuDebugFile, sb.ToString());
                return;
            }

            var topItems = menuBar.FindAll(TreeScope.Children,
                new PropertyCondition(AutomationElement.ControlTypeProperty, ControlType.MenuItem));
            sb.AppendLine($"Top-level menu items: {topItems.Count}");

            foreach (AutomationElement topItem in topItems)
            {
                sb.AppendLine($"- \"{topItem.Current.Name}\" (AutomationId={topItem.Current.AutomationId})");
                try
                {
                    if (topItem.TryGetCurrentPattern(ExpandCollapsePattern.Pattern, out var patternObj)
                        && patternObj is ExpandCollapsePattern expandPattern)
                    {
                        expandPattern.Expand();
                        Thread.Sleep(400);

                        var subItems = topItem.FindAll(TreeScope.Descendants,
                            new PropertyCondition(AutomationElement.ControlTypeProperty, ControlType.MenuItem));
                        foreach (AutomationElement subItem in subItems)
                        {
                            sb.AppendLine($"    - \"{subItem.Current.Name}\" (AutomationId={subItem.Current.AutomationId})");
                        }

                        expandPattern.Collapse();
                        Thread.Sleep(200);
                    }
                    else
                    {
                        sb.AppendLine("    (item does not support Expand/Collapse - skipped, no click attempted)");
                    }
                }
                catch (Exception ex)
                {
                    sb.AppendLine($"    (error while expanding, no click attempted: {ex.Message})");
                }
            }

            File.WriteAllText(MenuDebugFile, sb.ToString());
            Logger.Information("AeroAdmin menu structure captured to {Path} for building real unattended-access automation", MenuDebugFile);
        }
        catch (Exception ex)
        {
            Logger.Debug(ex, "AeroAdmin menu dump failed (non-fatal, one-time diagnostic only)");
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
        //
        // תוקן (08/09, אומת מול aeroadmin-ui-debug.txt אמיתי מקיוסק): ב-AeroAdmin
        // v4.93 הערכים האלה לא יושבים ב-ControlType.Text בכלל אלא ב-ControlType.Pane
        // (למשל Name='832 796 561' AutomationId='10132') - זו הייתה הסיבה
        // האמיתית לכשל, לא בעיית שפה/regex. מחפשים גם וגם.
        var texts = mainWindow.FindAll(TreeScope.Descendants,
            new OrCondition(
                new PropertyCondition(AutomationElement.ControlTypeProperty, ControlType.Text),
                new PropertyCondition(AutomationElement.ControlTypeProperty, ControlType.Pane)));
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
        // תוקן (08/09) - ראו הערה ב-ReadOwnId: גם ה-PIN יושב ב-ControlType.Pane
        // ולא ב-Text בגרסה הזו (למשל Name='6214' AutomationId='10133').
        var texts = mainWindow.FindAll(TreeScope.Descendants,
            new OrCondition(
                new PropertyCondition(AutomationElement.ControlTypeProperty, ControlType.Text),
                new PropertyCondition(AutomationElement.ControlTypeProperty, ControlType.Pane)));
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
