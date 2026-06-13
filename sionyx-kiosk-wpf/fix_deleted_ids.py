content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', encoding='utf-8').read()

# Add field
old = "    private List<KioskMessageItem> _adminMessages = new();"
new = "    private List<KioskMessageItem> _adminMessages = new();\n    private readonly HashSet<string> _deletedIds = new();"

count = content.count(old)
print(f"Found field: {count}")
if count == 1:
    content = content.replace(old, new, 1)

# Load deleted IDs on page load
old = "        var result = await _chat.GetAllMessagesAsync();"
new = """        // Load deleted IDs from local DB
        var deletedRaw = _localDb.Get("deleted_message_ids");
        if (!string.IsNullOrEmpty(deletedRaw))
            foreach (var id in deletedRaw.Split(','))
                if (!string.IsNullOrWhiteSpace(id)) _deletedIds.Add(id.Trim());

        var result = await _chat.GetAllMessagesAsync();"""

count2 = content.count(old)
print(f"Found load: {count2}")
if count2 == 1:
    content = content.replace(old, new, 1)

open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', 'w', encoding='utf-8').write(content)
print('Done')
