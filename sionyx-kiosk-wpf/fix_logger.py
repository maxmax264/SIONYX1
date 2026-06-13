content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', encoding='utf-8').read()

old = '            Logger.Information("[DELETE] msgId={MsgId} isReply={IsReply}", msgId, msgId.StartsWith("reply_"));'
new = '            Serilog.Log.Information("[DELETE] msgId={MsgId} isReply={IsReply}", msgId, msgId.StartsWith("reply_"));'

count = content.count(old)
print(f"Found: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', 'w', encoding='utf-8').write(content)
    print('Done')
else:
    print('NOT FOUND')
