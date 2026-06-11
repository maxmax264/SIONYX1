content = open(r'.\src\SionyxKiosk\Services\ChatService.cs', encoding='utf-8').read()
old = """    // ==================== PRIVATE ===================="""
new = """    /// <summary>Get replies sent by the current user from userReplies node.</summary>
    public async Task<ServiceResult> GetUserRepliesAsync()
    {
        var result = await Firebase.DbGetAsync("userReplies");
        if (!result.IsSuccess) return Success(new List<Dictionary<string, object?>>());

        var replies = new List<Dictionary<string, object?>>();
        if (result.Data is System.Text.Json.JsonElement data && data.ValueKind == System.Text.Json.JsonValueKind.Object)
        {
            foreach (var prop in data.EnumerateObject())
            {
                if (prop.Value.ValueKind != System.Text.Json.JsonValueKind.Object) continue;
                var fromUser = prop.Value.TryGetProperty("fromUserId", out var fu) ? fu.GetString() : null;
                if (fromUser != _userId) continue;

                var reply = new Dictionary<string, object?> { ["id"] = prop.Name, ["isUserReply"] = true };
                foreach (var field in prop.Value.EnumerateObject())
                    reply[field.Name] = field.Value.ValueKind switch
                    {
                        System.Text.Json.JsonValueKind.String => field.Value.GetString(),
                        System.Text.Json.JsonValueKind.True => true,
                        System.Text.Json.JsonValueKind.False => false,
                        System.Text.Json.JsonValueKind.Number => field.Value.GetDouble(),
                        _ => field.Value.ToString(),
                    };
                replies.Add(reply);
            }
        }

        replies.Sort((a, b) =>
        {
            var ta = a.TryGetValue("timestamp", out var va) ? va?.ToString() ?? "" : "";
            var tb = b.TryGetValue("timestamp", out var vb) ? vb?.ToString() ?? "" : "";
            return string.Compare(ta, tb, StringComparison.Ordinal);
        });

        return Success(replies);
    }

    // ==================== PRIVATE ===================="""
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\ChatService.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
