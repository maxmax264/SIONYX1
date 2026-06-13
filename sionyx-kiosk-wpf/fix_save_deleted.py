content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', encoding='utf-8').read()

# Save deleted ID
old = """            Serilog.Log.Information("[DELETE] msgId={MsgId} isReply={IsReply}", msgId, msgId.StartsWith("reply_"));
            var isReply = msgId.StartsWith("reply_");
            var path = isReply ? $"userReplies/{msgId}" : $"messages/{msgId}";
            var result = await _firebase.DbDeleteAsync(path);
            if (result.Success)
            {
                _adminMessages.RemoveAll(m => m.Id == msgId);
                _supervisorMessages.RemoveAll(m => m.Id == msgId);
                UpdateAdminUI();
                UpdateSupervisorUI();
            }"""

new = """            Serilog.Log.Information("[DELETE] msgId={MsgId} isReply={IsReply}", msgId, msgId.StartsWith("reply_"));
            var isReply = msgId.StartsWith("reply_");
            var path = isReply ? $"userReplies/{msgId}" : $"messages/{msgId}";
            await _firebase.DbDeleteAsync(path);
            _deletedIds.Add(msgId);
            var existing = _localDb.Get("deleted_message_ids") ?? "";
            _localDb.Set("deleted_message_ids", string.IsNullOrEmpty(existing) ? msgId : existing + "," + msgId);
            _adminMessages.RemoveAll(m => m.Id == msgId);
            _supervisorMessages.RemoveAll(m => m.Id == msgId);
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
