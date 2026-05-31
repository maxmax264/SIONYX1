namespace SionyxKiosk.Models;

public class PrintLogItem
{
    public string Timestamp { get; set; } = "";
    public string DocName { get; set; } = "";
    public int Pages { get; set; }
    public double Cost { get; set; }
    public string PrinterName { get; set; } = "";

    public string CostDisplay => $"₪{Cost:F2}";
    public string TimestampDisplay
    {
        get
        {
            if (DateTime.TryParse(Timestamp, out var dt))
                return dt.ToString("dd/MM/yyyy HH:mm");
            return Timestamp;
        }
    }
}
