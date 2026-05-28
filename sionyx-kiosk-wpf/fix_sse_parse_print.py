content = open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', encoding='utf-8').read()

old = '''            if (data.Value.ValueKind == JsonValueKind.Null) return;
            double newBalance;
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
new = '''            if (data.Value.ValueKind == JsonValueKind.Null) return;
            var payload = data.Value;
            if (payload.ValueKind == JsonValueKind.Object && payload.TryGetProperty("data", out var inner))
                payload = inner;
            if (payload.ValueKind == JsonValueKind.Null) return;
            double newBalance;
            if (payload.ValueKind == JsonValueKind.Number)
            {
                if (!payload.TryGetDouble(out newBalance)) return;
            }
            else if (payload.ValueKind == JsonValueKind.Object &&
                     payload.TryGetProperty("printBalance", out var pb))
            {
                if (!pb.TryGetDouble(out newBalance)) return;
            }
            else return;'''

count = content.count(old)
print(f"PrintMonitorService matches: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', 'w', encoding='utf-8').write(content)
    print('PrintMonitorService: OK')
else:
    idx = content.find('OnPrintBalanceUpdated')
    print(repr(content[idx:idx+300]))
