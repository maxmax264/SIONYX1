# Fix PrintMonitorService
content = open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', encoding='utf-8').read()
old = '''            if (!data.Value.TryGetDouble(out var newBalance)) return;'''
new = '''            double newBalance;
            if (data.Value.ValueKind == JsonValueKind.Number)
            {
                if (!data.Value.TryGetDouble(out newBalance)) return;
            }
            else if (data.Value.ValueKind == JsonValueKind.Object &&
                     data.Value.TryGetProperty("printBalance", out var pb))
            {
                if (!pb.TryGetDouble(out newBalance)) return;
            }
            else return;'''
if old in content:
    open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', 'w', encoding='utf-8').write(content.replace(old, new, 1))
    print('PrintMonitorService: OK')
else:
    print('PrintMonitorService: NOT FOUND')

# Fix SessionService
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
if old in content:
    open(r'.\src\SionyxKiosk\Services\SessionService.cs', 'w', encoding='utf-8').write(content.replace(old, new, 1))
    print('SessionService: OK')
else:
    print('SessionService: NOT FOUND')
