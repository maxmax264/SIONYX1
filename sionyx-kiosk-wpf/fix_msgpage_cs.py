content = """using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using Serilog;
using SionyxKiosk.Services;
using SionyxKiosk.Infrastructure;

namespace SionyxKiosk.Views.Pages;

public class KioskMessageItem
{
    public string Id { get; set; } = "";
    public string SenderName { get; set; } = "";
    public string DisplayBody { get; set; } = "";
    public string DisplayTime { get; set; } = "";
    public long RawTimestamp { get; set; }
    public bool FromSupervisor { get; set; }
}

public partial class MessagesPage : Page
{
    private readonly ChatService _chat;
    private readonly FirebaseClient _firebase;
    private string _adminDisplayName = "\u05de\u05e0\u05d4\u05dc";
    private string _supervisorDisplayName = "\u05e4\u05d9\u05e7\u05d5\u05d7";
    private List<KioskMessageItem> _adminMessages = new();
    private List<KioskMessageItem> _supervisorMessages = new();

    public MessagesPage(ChatService chat, FirebaseClient firebase)
    {
        _chat = chat;
        _firebase = firebase;
        InitializeComponent();
        Loaded += OnLoaded;
    }

    private async void OnLoaded(object sender, RoutedEventArgs e)
    {
        await LoadDisplayNamesAsync();
        await LoadMessagesAsync();
        UpdateTabHeaders();
    }

    private async Task LoadDisplayNamesAsync()
    {
        try
        {
            var nameResult = await _firebase.DbGetAsync($"metadata/settings/displayName");
            if (nameResult.Success && nameResult.Data is System.Text.Json.JsonElement el
                && el.ValueKind == System.Text.Json.JsonValueKind.String)
            {
                var name = el.GetString();
                if (!string.IsNullOrWhiteSpace(name)) _adminDisplayName = name;
            }
        }
        catch (Exception ex) { Log.Warning(ex, "Could not load admin display name"); }
    }

    private async Task LoadMessagesAsync()
    {
        AdminLoadingPanel.Visibility = Visibility.Visible;
        AdminScroll.Visibility = Visibility.Collapsed;
        AdminEmptyPanel.Visibility = Visibility.Collapsed;
        SupervisorLoadingPanel.Visibility = Visibility.Visible;
        SupervisorScroll.Visibility = Visibility.Collapsed;
        SupervisorEmptyPanel.Visibility = Visibility.Collapsed;

        try
        {
            var result = await _chat.GetUnreadMessagesAsync(useCache: false);
            if (!result.IsSuccess) return;

            var allMsgs = (List<Dictionary<string, object?>>)result.Data!;
            _adminMessages = new();
            _supervisorMessages = new();

            foreach (var msg in allMsgs)
            {
                var fromSupervisor = msg.TryGetValue("fromSupervisor", out var fs) && fs is bool b && b;
                var body = msg.TryGetValue("message", out var m) ? m?.ToString() ?? "" : "";
                var id = msg.TryGetValue("id", out var mid) ? mid?.ToString() ?? "" : "";
                long rawTs = 0;
                string timeDisplay = "";
                if (msg.TryGetValue("timestamp", out var ts))
                {
                    if (ts is double d) rawTs = (long)d;
                    else if (ts is string s && long.TryParse(s, out var p)) rawTs = p;
                    if (rawTs > 0)
                    {
                        var dt = DateTimeOffset.FromUnixTimeMilliseconds(rawTs).LocalDateTime;
                        var now = DateTime.Now;
                        timeDisplay = dt.Date == now.Date ? dt.ToString("HH:mm")
                            : dt.Date == now.Date.AddDays(-1) ? $"\u05d0\u05ea\u05de\u05d5\u05dc {dt:HH:mm}"
                            : dt.ToString("dd/MM HH:mm");
                    }
                }

                // Try load supervisor display name
                string senderName;
                if (fromSupervisor)
                {
                    senderName = $"\u05e4\u05d9\u05e7\u05d5\u05d7 {_supervisorDisplayName}";
                    var fromId = msg.TryGetValue("fromAdminId", out var fid) ? fid?.ToString() ?? "" : "";
                    if (!string.IsNullOrEmpty(fromId))
                    {
                        try
                        {
                            var supResult = await _firebase.DbGetAsync($"supervisors/{fromId}/displayName");
                            if (supResult.Success && supResult.Data is System.Text.Json.JsonElement se
                                && se.ValueKind == System.Text.Json.JsonValueKind.String)
                            {
                                var sn = se.GetString();
                                if (!string.IsNullOrWhiteSpace(sn)) senderName = $"\u05e4\u05d9\u05e7\u05d5\u05d7 {sn}";
                            }
                        }
                        catch { }
                    }
                }
                else
                {
                    senderName = _adminDisplayName;
                }

                var item = new KioskMessageItem
                {
                    Id = id, SenderName = senderName, DisplayBody = body,
                    DisplayTime = timeDisplay, RawTimestamp = rawTs, FromSupervisor = fromSupervisor
                };

                if (fromSupervisor) _supervisorMessages.Add(item);
                else _adminMessages.Add(item);
            }

            UpdateAdminUI();
            UpdateSupervisorUI();
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to load messages");
        }
    }

    private void UpdateAdminUI()
    {
        AdminLoadingPanel.Visibility = Visibility.Collapsed;
        if (_adminMessages.Count == 0)
        {
            AdminEmptyPanel.Visibility = Visibility.Visible;
            AdminScroll.Visibility = Visibility.Collapsed;
        }
        else
        {
            AdminEmptyPanel.Visibility = Visibility.Collapsed;
            AdminScroll.Visibility = Visibility.Visible;
            AdminMessagesList.ItemsSource = _adminMessages.OrderBy(m => m.RawTimestamp).ToList();
            AdminScroll.ScrollToEnd();
        }
    }

    private void UpdateSupervisorUI()
    {
        SupervisorLoadingPanel.Visibility = Visibility.Collapsed;
        if (_supervisorMessages.Count == 0)
        {
            SupervisorEmptyPanel.Visibility = Visibility.Visible;
            SupervisorScroll.Visibility = Visibility.Collapsed;
        }
        else
        {
            SupervisorEmptyPanel.Visibility = Visibility.Collapsed;
            SupervisorScroll.Visibility = Visibility.Visible;
            SupervisorMessagesList.ItemsSource = _supervisorMessages.OrderBy(m => m.RawTimestamp).ToList();
            SupervisorScroll.ScrollToEnd();
        }
    }

    private void UpdateTabHeaders()
    {
        var adminCount = _adminMessages.Count;
        var supCount = _supervisorMessages.Count;
        AdminTab.Header = adminCount > 0 ? $"\u05d4\u05d5\u05d3\u05e2\u05d5\u05ea \u05de\u05de\u05e0\u05d4\u05dc ({adminCount})" : "\u05d4\u05d5\u05d3\u05e2\u05d5\u05ea \u05de\u05de\u05e0\u05d4\u05dc";
        SupervisorTab.Header = supCount > 0 ? $"\u05d4\u05d5\u05d3\u05e2\u05d5\u05ea \u05de\u05d4\u05e4\u05d9\u05e7\u05d5\u05d7 ({supCount})" : "\u05d4\u05d5\u05d3\u05e2\u05d5\u05ea \u05de\u05d4\u05e4\u05d9\u05e7\u05d5\u05d7";
    }

    private async void AdminSendBtn_Click(object sender, RoutedEventArgs e)
    {
        var text = AdminReplyBox.Text.Trim();
        if (string.IsNullOrEmpty(text)) return;
        await SendReplyAsync(text, false);
        AdminReplyBox.Text = "";
    }

    private async void SupervisorSendBtn_Click(object sender, RoutedEventArgs e)
    {
        var text = SupervisorReplyBox.Text.Trim();
        if (string.IsNullOrEmpty(text)) return;
        await SendReplyAsync(text, true);
        SupervisorReplyBox.Text = "";
    }

    private async Task SendReplyAsync(string text, bool toSupervisor)
    {
        try
        {
            var userId = _firebase.UserId;
            var orgId = _firebase.OrgId;
            if (string.IsNullOrEmpty(userId) || string.IsNullOrEmpty(orgId)) return;

            var replyData = new
            {
                fromUserId = userId,
                toAdminId = "admin",
                fromSupervisorReply = toSupervisor,
                message = text,
                timestamp = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(),
                read = false,
                isUserReply = true,
            };

            await _firebase.DbPushAsync($"organizations/{orgId}/userReplies", replyData);

            Views.Controls.FloatingNotification.Show(
                toSupervisor ? "\u05ea\u05d2\u05d5\u05d1\u05d4 \u05e0\u05e9\u05dc\u05d7\u05d4 \u05dc\u05e4\u05d9\u05e7\u05d5\u05d7"
                             : "\u05ea\u05d2\u05d5\u05d1\u05d4 \u05e0\u05e9\u05dc\u05d7\u05d4 \u05dc\u05de\u05e0\u05d4\u05dc",
                text.Length > 40 ? text[..40] + "..." : text,
                Views.Controls.FloatingNotification.NotificationType.Success, 3000);
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to send reply");
        }
    }
}
"""

open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', 'w', encoding='utf-8').write(content)
print('OK')
