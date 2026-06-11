content = open(r'.\src\SionyxKiosk\Services\ChatService.cs', encoding='utf-8').read()
old = '''    public async Task<ServiceResult> GetAllMessagesAsync(bool useCache = false)
    {
        var result = await Firebase.DbGetAsync("messages");
        if (!result.IsSuccess) return result;
        return Success(ExtractUserMessages(result.Data, includeRead: true));
    }'''
new = '''    public async Task<ServiceResult> GetAllMessagesAsync()
    {
        var result = await Firebase.DbGetAsync("messages");
        if (!result.Success) return Error(result.Error ?? "Failed to fetch messages");
        if (result.Data is JsonElement data && data.ValueKind == JsonValueKind.Object)
        {
            var messages = ExtractUserMessages(data, includeRead: true);
            return Success(messages);
        }
        return Success(new List<Dictionary<string, object?>>());
    }'''
count = content.count(old)
print(f"Found {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\ChatService.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
