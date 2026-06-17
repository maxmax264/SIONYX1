using System;
using System.IO;

internal static class SionyxLogger
{
    private static readonly string LogDir = @"C:\Users\Public\Documents\SIONYX\logs";
    private static readonly string LogFile = Path.Combine(LogDir, "install.log");

    public static void Log(string message)
    {
        try
        {
            Directory.CreateDirectory(LogDir);
            string line = $"[{DateTime.Now:yyyy-MM-dd HH:mm:ss}] {message}";
            File.AppendAllText(LogFile, line + Environment.NewLine);
        }
        catch
        {
            // לא נכשל את ההתקנה בגלל לוג
        }
    }
}
