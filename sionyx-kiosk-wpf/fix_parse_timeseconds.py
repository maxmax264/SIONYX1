f = open(r'.\src\SionyxKiosk\Services\PurchaseService.cs', encoding='utf-8')
c = f.read()
f.close()

old = '        Note = el.TryGetProperty("note", out var n) ? n.GetString() ?? "" : "",\n    };'
new = '        Note = el.TryGetProperty("note", out var n) ? n.GetString() ?? "" : "",\n        TimeSeconds = el.TryGetProperty("timeSeconds", out var ts) && ts.TryGetInt32(out var tsv) ? tsv : 0,\n    };'

count = c.count(old)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\PurchaseService.cs', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
