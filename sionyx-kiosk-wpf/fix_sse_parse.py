content = open(r'.\src\SionyxKiosk\Services\SessionService.cs', encoding='utf-8').read()

old = '''    private void OnRemainingTimeUpdated(string eventType, JsonElement? data)
    {
        if (eventType != "put" || data == null) return;
        try
        {
            Logger.Information("[SSE-DEBUG] remainingTime event: type={Type} kind={Kind} first={First} data={Data}", eventType, data.Value.ValueKind, _isFirstRemainingTimeEvent, data.Value.ToString());
            if (_isFirstRemainingTimeEvent) { _isFirstRemainingTimeEvent = false; return; }
            if (data.Value.ValueKind == JsonValueKind.Null) return;
            int newTime;
            if (data.Value.ValueKind == JsonValueKind.Number)
            {
                if (!data.Value.TryGetInt32(out newTime)) return;
            }
            else if (data.Value.ValueKind == JsonValueKind.Object &&
                     data.Value.TryGetProperty("remainingTime", out var rt))
            {
                if (!rt.TryGetInt32(out newTime)) return;
            }
            else return;'''
new = '''    private void OnRemainingTimeUpdated(string eventType, JsonElement? data)
    {
        if (eventType != "put" || data == null) return;
        try
        {
            if (_isFirstRemainingTimeEvent) { _isFirstRemainingTimeEvent = false; return; }
            if (data.Value.ValueKind == JsonValueKind.Null) return;
            var payload = data.Value;
            if (payload.ValueKind == JsonValueKind.Object && payload.TryGetProperty("data", out var inner))
                payload = inner;
            if (payload.ValueKind == JsonValueKind.Null) return;
            int newTime;
            if (payload.ValueKind == JsonValueKind.Number)
            {
                if (!payload.TryGetInt32(out newTime)) return;
            }
            else if (payload.ValueKind == JsonValueKind.Object &&
                     payload.TryGetProperty("remainingTime", out var rt))
            {
                if (!rt.TryGetInt32(out newTime)) return;
            }
            else return;'''

count = content.count(old)
print(f"SessionService matches: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\SessionService.cs', 'w', encoding='utf-8').write(content)
    print('SessionService: OK')
else:
    idx = content.find('OnRemainingTimeUpdated')
    print(repr(content[idx:idx+300]))
