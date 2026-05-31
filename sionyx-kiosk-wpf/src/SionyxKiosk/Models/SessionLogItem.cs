namespace SionyxKiosk.Models;

public class SessionLogItem
{
    public string EndTime { get; set; } = "";
    public string ComputerName { get; set; } = "";
    public int UsedSeconds { get; set; }
    public string Reason { get; set; } = "";

    public string UsedMinutesDisplay => UsedSeconds > 0 ? $"{UsedSeconds / 60} דק'" : "-";
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
