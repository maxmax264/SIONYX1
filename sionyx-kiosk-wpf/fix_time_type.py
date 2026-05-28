content = open(r'.\src\SionyxKiosk\Services\SessionService.cs', encoding='utf-8').read()
old = '''            if (!data.Value.TryGetInt32(out var newTime)) return;'''
new = '''            int newTime;
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
content = content.replace(old, new, 1)
open(r'.\src\SionyxKiosk\Services\SessionService.cs', 'w', encoding='utf-8').write(content)
print('OK')
