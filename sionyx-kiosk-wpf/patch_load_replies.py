content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', encoding='utf-8').read()

old = """            UpdateAdminUI();
            UpdateSupervisorUI();"""

new = """            // Load user replies from Firebase
            var repliesResult = await _firebase.DbGetAsync($"organizations/{_firebase.OrgId}/userReplies");
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
                            : dt.Date == now2.Date.AddDays(-1) ? $"אתמול {dt:HH:mm}"
                            : dt.ToString("dd/MM HH:mm");
                    }
                    var replyItem = new KioskMessageItem
                    {
                        Id = prop.Name,
                        SenderName = "אתה",
                        DisplayBody = replyBody,
                        DisplayTime = replyTime,
                        RawTimestamp = replyTs,
                        FromSupervisor = isSupervisorReply,
                        IsUserReply = true
                    };
                    if (isSupervisorReply) _supervisorMessages.Add(replyItem);
                    else _adminMessages.Add(replyItem);
                }
                _adminMessages = _adminMessages.OrderBy(m => m.RawTimestamp).ToList();
                _supervisorMessages = _supervisorMessages.OrderBy(m => m.RawTimestamp).ToList();
            }

            UpdateAdminUI();
            UpdateSupervisorUI();"""

count = content.count(old)
print(f"Found: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', 'w', encoding='utf-8').write(content)
    print('Done')
else:
    print('NOT FOUND')
