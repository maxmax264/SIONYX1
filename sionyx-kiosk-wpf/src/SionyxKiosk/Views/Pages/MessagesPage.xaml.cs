using System.Windows;
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
    public bool IsUserReply { get; set; }
}

public partial class MessagesPage : Page
{
    private readonly ChatService _chat;
    private readonly FirebaseClient _firebase;
    private readonly LocalDatabase _localDb;
    private string _adminDisplayName = "׳׳ ׳”׳";
    private string _supervisorDisplayName = "׳₪׳™׳§׳•׳—";
    private List<KioskMessageItem> _adminMessages = new();
    private readonly HashSet<string> _deletedIds = new();
    private List<KioskMessageItem> _supervisorMessages = new();

    public MessagesPage(ChatService chat, FirebaseClient firebase, LocalDatabase localDb)
    {
        _chat = chat;
        _firebase = firebase;
        _localDb = localDb;
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

    private async void DeleteMessage_Click(object sender, System.Windows.RoutedEventArgs e)
    {
        if (sender is System.Windows.Controls.Button btn && btn.Tag is string msgId)
        {
            Serilog.Log.Information("[DELETE] msgId={MsgId} isReply={IsReply}", msgId, msgId.StartsWith("reply_"));
            var isReply = msgId.StartsWith("reply_");
            var path = isReply ? $"userReplies/{msgId}" : $"messages/{msgId}";
            await _firebase.DbDeleteAsync(path);
            _deletedIds.Add(msgId);
            var existing = _localDb.Get("deleted_message_ids") ?? "";
            _localDb.Set("deleted_message_ids", string.IsNullOrEmpty(existing) ? msgId : existing + "," + msgId);
            _adminMessages.RemoveAll(m => m.Id == msgId);
            _supervisorMessages.RemoveAll(m => m.Id == msgId);
            UpdateAdminUI();
            UpdateSupervisorUI();
        }
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
            // Load deleted IDs from local DB
        var deletedRaw = _localDb.Get("deleted_message_ids");
        if (!string.IsNullOrEmpty(deletedRaw))
            foreach (var id in deletedRaw.Split(','))
                if (!string.IsNullOrWhiteSpace(id)) _deletedIds.Add(id.Trim());

        var result = await _chat.GetAllMessagesAsync();
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
                            : dt.Date == now.Date.AddDays(-1) ? $"׳׳×׳׳•׳ {dt:HH:mm}"
                            : dt.ToString("dd/MM HH:mm");
                    }
                }

                // Try load supervisor display name
                string senderName;
                if (fromSupervisor)
                {
                    senderName = $"׳₪׳™׳§׳•׳— {_supervisorDisplayName}";
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
                                if (!string.IsNullOrWhiteSpace(sn)) senderName = $"׳₪׳™׳§׳•׳— {sn}";
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

                if (_deletedIds.Contains(id)) continue;
                if (fromSupervisor) _supervisorMessages.Add(item);
                else _adminMessages.Add(item);
            }

            // Load user replies from Firebase
            var repliesResult = await _firebase.DbGetAsync($"userReplies");
            if (repliesResult.Success && repliesResult.Data is System.Text.Json.JsonElement repliesEl
                && repliesEl.ValueKind == System.Text.Json.JsonValueKind.Object)
            {
                foreach (var prop in repliesEl.EnumerateObject())
                {
                    var r = prop.Value;
                    var fromUserId = r.TryGetProperty("fromUserId", out var fuid) ? fuid.GetString() ?? "" : "";
                    if (fromUserId != _firebase.UserId) continue;
                    var replyBody = r.TryGetProperty("message", out var rm) ? rm.GetString() ?? "" : "";
                    var isSupervisorReply = r.TryGetProperty("fromSupervisorReply", out var fsr) && fsr.GetBoolean();
                    long replyTs = 0;
                    if (r.TryGetProperty("timestamp", out var rts)) replyTs = rts.GetInt64();
                    string replyTime = "";
                    if (replyTs > 0)
                    {
                        var dt = DateTimeOffset.FromUnixTimeMilliseconds(replyTs).LocalDateTime;
                        var now2 = DateTime.Now;
                        replyTime = dt.Date == now2.Date ? dt.ToString("HH:mm")
                            : dt.Date == now2.Date.AddDays(-1) ? $"׳׳×׳׳•׳ {dt:HH:mm}"
                            : dt.ToString("dd/MM HH:mm");
                    }
                    var replyItem = new KioskMessageItem
                    {
                        Id = prop.Name,
                        SenderName = "׳׳×׳”",
                        DisplayBody = replyBody,
                        DisplayTime = replyTime,
                        RawTimestamp = replyTs,
                        FromSupervisor = isSupervisorReply,
                        IsUserReply = true
                    };
                    if (_deletedIds.Contains(prop.Name)) continue;
                    if (isSupervisorReply) _supervisorMessages.Add(replyItem);
                    else _adminMessages.Add(replyItem);
                }
                _adminMessages = _adminMessages.OrderBy(m => m.RawTimestamp).ToList();
                _supervisorMessages = _supervisorMessages.OrderBy(m => m.RawTimestamp).ToList();
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
        AdminTab.Header = adminCount > 0 ? $"׳”׳•׳“׳¢׳•׳× ׳׳׳ ׳”׳ ({adminCount})" : "׳”׳•׳“׳¢׳•׳× ׳׳׳ ׳”׳";
        SupervisorTab.Header = supCount > 0 ? $"׳”׳•׳“׳¢׳•׳× ׳׳”׳₪׳™׳§׳•׳— ({supCount})" : "׳”׳•׳“׳¢׳•׳× ׳׳”׳₪׳™׳§׳•׳—";
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
            Log.Information("SendReply: userId={UserId} orgId={OrgId} text={Text}", userId, orgId, text);
            if (string.IsNullOrEmpty(userId) || string.IsNullOrEmpty(orgId))
            {
                Log.Warning("SendReply: userId or orgId is empty, aborting");
                return;
            }

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

            var replyKey = $"reply_{DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()}_{userId[..8]}";
            var pushResult = await _firebase.DbSetAsync($"userReplies/{replyKey}", replyData);
            Log.Information("SendReply result: Success={Success} Error={Error}", pushResult.Success, pushResult.Error);

            // Add reply locally so it appears immediately in the UI
            var now = DateTimeOffset.Now;
            var replyItem = new KioskMessageItem
            {
                Id = replyKey,
                SenderName = "׳׳×׳”",
                DisplayBody = text,
                DisplayTime = now.ToString("HH:mm"),
                RawTimestamp = now.ToUnixTimeMilliseconds(),
                FromSupervisor = toSupervisor,
                IsUserReply = true
            };
            if (toSupervisor) { _supervisorMessages.Add(replyItem); UpdateSupervisorUI(); }
            else { _adminMessages.Add(replyItem); UpdateAdminUI(); }

            Views.Controls.FloatingNotification.Show(
                toSupervisor ? "׳×׳’׳•׳‘׳” ׳ ׳©׳׳—׳” ׳׳₪׳™׳§׳•׳—"
                             : "׳×׳’׳•׳‘׳” ׳ ׳©׳׳—׳” ׳׳׳ ׳”׳",
                text.Length > 40 ? text[..40] + "..." : text,
                Views.Controls.FloatingNotification.NotificationType.Success, 3000);
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to send reply");
        }
    }
}

