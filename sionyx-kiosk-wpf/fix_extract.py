content = open(r'.\src\SionyxKiosk\Services\ChatService.cs', encoding='utf-8').read()

# Fix the injected GetAllMessagesAsync to not pass filterUnread param
old1 = '        return Success(ExtractUserMessages(result.Data, filterUnread: false));'
new1 = '        return Success(ExtractUserMessages(result.Data, includeRead: true));'
c1 = content.count(old1)
print(f"Fix call: {c1}")
if c1 == 1:
    content = content.replace(old1, new1, 1)

# Add overload - change signature of existing method
old2 = '    private List<Dictionary<string, object?>> ExtractUserMessages(JsonElement allMessages)'
new2 = '    private List<Dictionary<string, object?>> ExtractUserMessages(JsonElement allMessages, bool includeRead = false)'
c2 = content.count(old2)
print(f"Fix signature: {c2}")
if c2 == 1:
    content = content.replace(old2, new2, 1)

# Fix the filter line
old3 = '            if (toUser == _userId && !isRead)'
new3 = '            if (toUser == _userId && (!isRead || includeRead))'
c3 = content.count(old3)
print(f"Fix filter: {c3}")
if c3 == 1:
    content = content.replace(old3, new3, 1)

open(r'.\src\SionyxKiosk\Services\ChatService.cs', 'w', encoding='utf-8').write(content)
print('Done')
