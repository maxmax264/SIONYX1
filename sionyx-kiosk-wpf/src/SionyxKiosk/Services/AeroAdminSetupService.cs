private void RunSetup()
{
    Process? process = null;
    try
    {
        // שינוי קריטי: WindowStyle=Normal, לא Hidden. הרצה ידנית (לחיצה
        // כפולה) הוכיחה שAeroAdmin פותח חלון תקין ומיידי - אבל עם
        // WindowStyle=Hidden דרך ProcessStartInfo, החלון הראשי כנראה לא
        // נוצר בכלל (תוכנות remote-access רבות "מדלגות" על יצירת UI כשהן
        // מזהות בקשת הפעלה מוסתרת, ונכנסות ישר למצב tray-only). לכן: מפעילים
        // גלוי בדיוק כמו הרצה ידנית - ומסתירים בעצמנו ברגע שיש handle תקף.
        var psi = new ProcessStartInfo(ExePath)
        {
            UseShellExecute = true,
            WindowStyle = ProcessWindowStyle.Normal,
        };
        process = Process.Start(psi);
        if (process == null)
        {
            Logger.Warning("Failed to start AeroAdmin.exe");
            return;
        }

        var handle = WaitForMainWindowHandle(process);
        if (handle == IntPtr.Zero)
        {
            Logger.Warning("AeroAdmin main window did not appear within {Timeout}s - cannot read ID/set password", WindowTimeout.TotalSeconds);
            DumpFailureDiagnostics(process);
            return;
        }

        // מסתירים מיד - לפני שהלקוח בקופה מספיק לראות משהו
        ShowWindow(handle, SW_HIDE);

        AutomationElement mainWindow;
        try
        {
            mainWindow = AutomationElement.FromHandle(handle);
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "Could not attach UI Automation to AeroAdmin window handle");
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
        // משאירים את AeroAdmin רץ ברקע (מוסתר) - זה מה שמאפשר חיבור
        // unattended מבחוץ; לא סוגרים את התהליך כאן.
        process?.Dispose();
    }
}

[DllImport("user32.dll")] private static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
[DllImport("user32.dll")] private static extern int GetWindowTextLength(IntPtr hWnd);
[DllImport("user32.dll", CharSet = CharSet.Auto)]
private static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder lpString, int nMaxCount);
private const int SW_HIDE = 0;

private static IntPtr WaitForMainWindowHandle(Process process)
{
    var deadline = DateTime.UtcNow + WindowTimeout;
    while (DateTime.UtcNow < deadline)
    {
        var handle = FindTopLevelWindowForProcess((uint)process.Id);
        if (handle != IntPtr.Zero) return handle;
        Thread.Sleep(300);
    }
    return IntPtr.Zero;
}

/// <summary>כשה-timeout פוקע בלי שנמצא חלון בכלל - עד עכשיו לא נכתב שום
/// דיבאג בנתיב הזה (בניגוד לשני נתיבי הכשל האחרים), אז לא היה לנו מושג
/// למה. כותבים כאן את מצב התהליך (רץ? קרס? קוד יציאה?) ורשימת כל החלונות
/// הפתוחים כרגע - כדי שבפעם הבאה שזה נכשל נדע בדיוק למה.</summary>
private static void DumpFailureDiagnostics(Process process)
{
    try
    {
        var sb = new System.Text.StringBuilder();
        sb.AppendLine($"[{DateTime.Now:yyyy-MM-dd HH:mm:ss}] AeroAdmin - main window not found within {WindowTimeout.TotalSeconds}s");
        bool exited;
        int? exitCode = null;
        try { exited = process.HasExited; if (exited) exitCode = process.ExitCode; }
        catch { exited = true; }
        sb.AppendLine($"process.Id={process.Id} HasExited={exited} ExitCode={exitCode?.ToString() ?? "N/A"}");
        sb.AppendLine("--- All top-level windows at time of failure ---");
        EnumWindows((hWnd, _) =>
        {
            GetWindowThreadProcessId(hWnd, out var pid);
            var len = GetWindowTextLength(hWnd);
            var title = new System.Text.StringBuilder(len + 1);
            GetWindowText(hWnd, title, title.Capacity);
            sb.AppendLine($"hWnd=0x{hWnd:X} pid={pid} title=\"{title}\"");
            return true;
        }, IntPtr.Zero);
        File.WriteAllText(UiDebugFile, sb.ToString());
    }
    catch (Exception ex)
    {
        Logger.Error(ex, "Failed to write AeroAdmin diagnostics dump");
    }
}
