content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', encoding='utf-8').read()

old = "    private readonly ChatService _chat;\n    private readonly FirebaseClient _firebase;"
new = "    private readonly ChatService _chat;\n    private readonly FirebaseClient _firebase;\n    private readonly LocalDatabase _localDb;"

count = content.count(old)
print(f"Found field: {count}")
if count == 1:
    content = content.replace(old, new, 1)

old2 = "    public MessagesPage(ChatService chat, FirebaseClient firebase)\n    {\n        _chat = chat;\n        _firebase = firebase;"
new2 = "    public MessagesPage(ChatService chat, FirebaseClient firebase, LocalDatabase localDb)\n    {\n        _chat = chat;\n        _firebase = firebase;\n        _localDb = localDb;"

count2 = content.count(old2)
print(f"Found ctor: {count2}")
if count2 == 1:
    content = content.replace(old2, new2, 1)

open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', 'w', encoding='utf-8').write(content)
print('Done')
