namespace SionyxKiosk.Models;

public class SessionLogItem
{
    public string EndTime { get; set; } = "";
    public string ComputerName { get; set; } = "";
    public int UsedSeconds { get; set; }
    public string Reason { get; set; } = "";

    public string UsedMinutesDisplay => UsedSeconds switch
    {
        <= 0 => "-",
        < 60 => $"{UsedSeconds} שנ'",
        < 3600 => $"{UsedSeconds / 60} דק'",
        _ => $"{UsedSeconds / 3600}:{(UsedSeconds % 3600) / 60:D2} שע'"
    };
    public string ReasonDisplay => Reason switch
    {
        "user" => "יציאה רגילה",
        "expired" => "נגמר זמן",
        "idle" => "חוסר פעילות",
        "hours" => "שעות פעילות",
        "hours_force" => "כיבוי כפוי",
        _ => Reason
    };
    public string EndTimeDisplay
    {
        get
        {
            if (DateTime.TryParse(EndTime, out var dt))
                return dt.ToString("dd/MM/yyyy HH:mm");
            return EndTime;
        }
    }
}
