content = open(r'.\src\SionyxKiosk\Services\ChatService.cs', encoding='utf-8').read()

# Step 1: revert
old1 = '            if (toUser == _userId)'
new1 = '            if (toUser == _userId && !isRead)'
count = content.count(old1)
print(f"Revert: Found {count}")
if count == 1:
    content = content.replace(old1, new1, 1)
    print('Reverted OK')

# Step 2: add GetAllMessagesAsync after GetUnreadMessagesAsync closing brace
old2 = '    /// <summary>Get all unread messages for the current user.</summary>'
new2 = '''    /// <summary>Get all messages for the current user (read and unread).</summary>
    public async Task<ServiceResult> GetAllMessagesAsync(bool useCache = false)
    {
        var result = await Firebase.DbGetAsync("messages");
        if (!result.IsSuccess) return result;
        return Success(ExtractUserMessages(result.Data, filterUnread: false));
    }

    /// <summary>Get all unread messages for the current user.</summary>'''
count2 = content.count(old2)
print(f"Inject: Found {count2}")
if count2 == 1:
    content = content.replace(old2, new2, 1)
    print('Injected OK')

open(r'.\src\SionyxKiosk\Services\ChatService.cs', 'w', encoding='utf-8').write(content)
