content = open(r'.\src\SionyxKiosk\Services\SessionService.cs', encoding='utf-8').read()

old = '            if (_isFirstRemainingTimeEvent) { _isFirstRemainingTimeEvent = false; return; }\n            if (data.Value.ValueKind == JsonValueKind.Null) return;'
new = '            Logger.Information("[SSE-DEBUG] remainingTime event: type={Type} kind={Kind} first={First} data={Data}", eventType, data.Value.ValueKind, _isFirstRemainingTimeEvent, data.Value.ToString());\n            if (_isFirstRemainingTimeEvent) { _isFirstRemainingTimeEvent = false; return; }\n            if (data.Value.ValueKind == JsonValueKind.Null) return;'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\SessionService.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
