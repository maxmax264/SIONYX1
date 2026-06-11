content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', encoding='utf-8').read()
old = '            var pushResult = await _firebase.DbPushAsync($"organizations/{orgId}/userReplies", replyData);\n            Log.Information("SendReply result: Success={Success} Error={Error}", pushResult.Success, pushResult.Error);'
new = '            var replyKey = $"reply_{DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()}_{userId[..8]}";\n            var pushResult = await _firebase.DbSetAsync($"userReplies/{replyKey}", replyData);\n            Log.Information("SendReply result: Success={Success} Error={Error}", pushResult.Success, pushResult.Error);'
count = content.count(old)
print(f"Found {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND - showing context')
    idx = content.find('SendReply result')
    print(repr(content[idx-200:idx+100]))
