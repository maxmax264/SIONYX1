content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', encoding='utf-8').read()
old = """public class KioskMessageItem
{
    public string Id { get; set; } = "";
    public string SenderName { get; set; } = "";
    public string DisplayBody { get; set; } = "";
    public string DisplayTime { get; set; } = "";
    public long RawTimestamp { get; set; }
    public bool FromSupervisor { get; set; }
}"""
new = """public class KioskMessageItem
{
    public string Id { get; set; } = "";
    public string SenderName { get; set; } = "";
    public string DisplayBody { get; set; } = "";
    public string DisplayTime { get; set; } = "";
    public long RawTimestamp { get; set; }
    public bool FromSupervisor { get; set; }
    public bool IsUserReply { get; set; }
    // Bubble alignment
    public System.Windows.HorizontalAlignment BubbleAlign =>
        IsUserReply ? System.Windows.HorizontalAlignment.Left : System.Windows.HorizontalAlignment.Right;
    public System.Windows.Media.Brush BubbleBg =>
        IsUserReply
            ? new System.Windows.Media.SolidColorBrush(System.Windows.Media.Color.FromRgb(240, 253, 244))
            : new System.Windows.Media.SolidColorBrush(System.Windows.Media.Color.FromRgb(237, 233, 254));
    public System.Windows.Media.Brush BubbleFg =>
        IsUserReply
            ? new System.Windows.Media.SolidColorBrush(System.Windows.Media.Color.FromRgb(5, 150, 105))
            : new System.Windows.Media.SolidColorBrush(System.Windows.Media.Color.FromRgb(67, 56, 202));
    public string SenderLabel => IsUserReply ? "את/ה" : SenderName;
}"""
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
