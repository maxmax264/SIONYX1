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
content = content.replace(old, new, 1)
open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', 'w', encoding='utf-8').write(content)
print('OK')
