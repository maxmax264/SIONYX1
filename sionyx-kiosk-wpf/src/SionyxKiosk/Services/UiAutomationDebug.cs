using System.IO;
using System.Windows.Automation;
using Serilog;

namespace SionyxKiosk.Services;

/// <summary>
/// כלי אבחון משותף ל-AeroAdminSetupService ול-TeamViewer UI Automation
/// (RemoteControlReportingService). ה-AutomationId/Name בשני המקומות האלה
/// לא אומתו מול ה-UI האמיתי (אין דרך להריץ Windows GUI מכאן) - אז כשהאוטומציה
/// נכשלת, במקום רק "Warning ולא כלום", כותבים את כל עץ ה-UI Automation לקובץ
/// טקסט. תוצאת הריצה הבאה על מכונה אמיתית נותנת את השמות/הטיפוסים האמיתיים
/// של הכפתורים/שדות, שאפשר לעדכן איתם את הקבועים בקוד - במקום ניחוש נוסף בעיוורון.
/// </summary>
internal static class UiAutomationDebug
{
    private static readonly ILogger Logger = Log.ForContext(typeof(UiAutomationDebug));

    public static void DumpTree(AutomationElement root, string outputPath, string context)
    {
        try
        {
            using var writer = new StreamWriter(outputPath, append: false, System.Text.Encoding.UTF8);
            writer.WriteLine($"# UI Automation tree dump - {context}");
            writer.WriteLine($"# {DateTimeOffset.Now:yyyy-MM-dd HH:mm:ss}");
            writer.WriteLine();
            Dump(root, writer, 0);
            Logger.Warning("{Context}: automation failed - full UI tree dumped to {Path} for diagnosis", context, outputPath);
        }
        catch (Exception ex)
        {
            Logger.Debug(ex, "Failed to write UI Automation debug dump to {Path}", outputPath);
        }
    }

    private static void Dump(AutomationElement element, StreamWriter writer, int depth)
    {
        if (depth > 8) return; // עומק בטיחות - נמנע מעץ אינסופי/ענק

        string controlType;
        string name;
        string automationId;
        try
        {
            var current = element.Current;
            controlType = current.ControlType.ProgrammaticName;
            name = current.Name ?? string.Empty;
            automationId = current.AutomationId ?? string.Empty;
        }
        catch
        {
            return; // אלמנט שהתייצב/נעלם באמצע הקריאה - מדלגים
        }

        var indent = new string(' ', depth * 2);
        writer.WriteLine($"{indent}[{controlType}] Name='{name}' AutomationId='{automationId}'");

        AutomationElementCollection children;
        try
        {
            children = element.FindAll(TreeScope.Children, Condition.TrueCondition);
        }
        catch
        {
            return;
        }

        foreach (AutomationElement child in children)
        {
            Dump(child, writer, depth + 1);
        }
    }
}
