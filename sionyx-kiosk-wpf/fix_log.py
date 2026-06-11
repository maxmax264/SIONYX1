content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', encoding='utf-8').read()
old = """            var userId = _firebase.UserId;
            var orgId = _firebase.OrgId;
            if (string.IsNullOrEmpty(userId) || string.IsNullOrEmpty(orgId)) return;"""
new = """            var userId = _firebase.UserId;
            var orgId = _firebase.OrgId;
            Log.Information("SendReply: userId={UserId} orgId={OrgId} text={Text}", userId, orgId, text);
            if (string.IsNullOrEmpty(userId) || string.IsNullOrEmpty(orgId))
            {
                Log.Warning("SendReply: userId or orgId is empty, aborting");
                return;
            }"""
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
