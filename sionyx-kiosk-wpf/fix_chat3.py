content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', encoding='utf-8').read()
old = """    private async Task LoadMessagesAsync()
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
                            : dt.Date == now.Date.AddDays(-1) ? $"אתמול {dt:HH:mm}"
                            : dt.ToString("dd/MM HH:mm");
                    }
                }

                // Try load supervisor display name
                string senderName;
                if (fromSupervisor)
                {
                    senderName = $"פיקוח {_supervisorDisplayName}";
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
                                if (!string.IsNullOrWhiteSpace(sn)) senderName = $"פיקוח {sn}";
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
    }"""
new = """    private async Task LoadMessagesAsync()
    {
        AdminLoadingPanel.Visibility = Visibility.Visible;
        AdminScroll.Visibility = Visibility.Collapsed;
        AdminEmptyPanel.Visibility = Visibility.Collapsed;
        SupervisorLoadingPanel.Visibility = Visibility.Visible;
        SupervisorScroll.Visibility = Visibility.Collapsed;
        SupervisorEmptyPanel.Visibility = Visibility.Collapsed;

        try
        {
            var msgsResult = await _chat.GetUnreadMessagesAsync(useCache: false);
            var repliesResult = await _chat.GetUserRepliesAsync();

            var allMsgs = msgsResult.IsSuccess ? (List<Dictionary<string, object?>>)msgsResult.Data! : new();
            var allReplies = repliesResult.IsSuccess ? (List<Dictionary<string, object?>>)repliesResult.Data! : new();

            _adminMessages = new();
            _supervisorMessages = new();

            // Helper to parse timestamp
            static long ParseTs(Dictionary<string, object?> msg)
            {
                if (!msg.TryGetValue("timestamp", out var ts)) return 0;
                if (ts is double d) return (long)d;
                if (ts is string s && long.TryParse(s, out var p)) return p;
                return 0;
            }

            static string FormatTs(long rawTs)
            {
                if (rawTs <= 0) return "";
                var dt = DateTimeOffset.FromUnixTimeMilliseconds(rawTs).LocalDateTime;
                var now = DateTime.Now;
                return dt.Date == now.Date ? dt.ToString("HH:mm")
                    : dt.Date == now.Date.AddDays(-1) ? $"אתמול {dt:HH:mm}"
                    : dt.ToString("dd/MM HH:mm");
            }

            // Process incoming messages
            foreach (var msg in allMsgs)
            {
                var fromSupervisor = msg.TryGetValue("fromSupervisor", out var fs) && fs is bool b && b;
                var body = msg.TryGetValue("message", out var m) ? m?.ToString() ?? "" : "";
                var id = msg.TryGetValue("id", out var mid) ? mid?.ToString() ?? "" : "";
                var rawTs = ParseTs(msg);

                string senderName;
                if (fromSupervisor)
                {
                    senderName = $"פיקוח {_supervisorDisplayName}";
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
                                if (!string.IsNullOrWhiteSpace(sn)) senderName = $"פיקוח {sn}";
                            }
                        }
                        catch { }
                    }
                }
                else senderName = _adminDisplayName;

                var item = new KioskMessageItem
                {
                    Id = id, SenderName = senderName, DisplayBody = body,
                    DisplayTime = FormatTs(rawTs), RawTimestamp = rawTs,
                    FromSupervisor = fromSupervisor, IsUserReply = false
                };

                if (fromSupervisor) _supervisorMessages.Add(item);
                else _adminMessages.Add(item);
            }

            // Process outgoing replies
            foreach (var reply in allReplies)
            {
                var toSupervisor = reply.TryGetValue("fromSupervisorReply", out var fsr) && fsr is bool bsr && bsr;
                var body = reply.TryGetValue("message", out var m) ? m?.ToString() ?? "" : "";
                var id = reply.TryGetValue("id", out var mid) ? mid?.ToString() ?? "" : "";
                var rawTs = ParseTs(reply);

                var item = new KioskMessageItem
                {
                    Id = id, SenderName = "את/ה", DisplayBody = body,
                    DisplayTime = FormatTs(rawTs), RawTimestamp = rawTs,
                    FromSupervisor = toSupervisor, IsUserReply = true
                };

                if (toSupervisor) _supervisorMessages.Add(item);
                else _adminMessages.Add(item);
            }

            // Sort by timestamp
            _adminMessages = _adminMessages.OrderBy(m => m.RawTimestamp).ToList();
            _supervisorMessages = _supervisorMessages.OrderBy(m => m.RawTimestamp).ToList();

            UpdateAdminUI();
            UpdateSupervisorUI();
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to load messages");
        }
    }"""
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
