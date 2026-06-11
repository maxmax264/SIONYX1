content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', encoding='utf-8').read()

old = '''            Views.Controls.FloatingNotification.Show(
                toSupervisor ? "תגובה נשלחה לפיקוח"
                             : "תגובה נשלחה למנהל",
                text.Length > 40 ? text[..40] + "..." : text,
                Views.Controls.FloatingNotification.NotificationType.Success, 3000);

            await LoadMessagesAsync();'''

new = '''            // Add reply locally so it appears immediately in the UI
            var now = DateTimeOffset.Now;
            var replyItem = new KioskMessageItem
            {
                Id = replyKey,
                SenderName = "אתה",
                DisplayBody = text,
                DisplayTime = now.ToString("HH:mm"),
                RawTimestamp = now.ToUnixTimeMilliseconds(),
                FromSupervisor = toSupervisor,
                IsUserReply = true
            };
            if (toSupervisor) { _supervisorMessages.Add(replyItem); UpdateSupervisorUI(); }
            else { _adminMessages.Add(replyItem); UpdateAdminUI(); }

            Views.Controls.FloatingNotification.Show(
                toSupervisor ? "תגובה נשלחה לפיקוח"
                             : "תגובה נשלחה למנהל",
                text.Length > 40 ? text[..40] + "..." : text,
                Views.Controls.FloatingNotification.NotificationType.Success, 3000);'''

count = content.count(old)
print(f"Found: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', 'w', encoding='utf-8').write(content)
    print('Done')
else:
    print('NOT FOUND')
