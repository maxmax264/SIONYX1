f = open(r'.\src\SionyxKiosk\Services\PurchaseService.cs', encoding='utf-8')
c = f.read()
f.close()

old = '        purchases.Sort((a, b) => string.Compare(b.CreatedAt, a.CreatedAt, StringComparison.Ordinal));'
new = '        purchases.Sort((a, b) => string.Compare(b.CreatedAt, a.CreatedAt, StringComparison.Ordinal));\n        foreach (var p in purchases) Serilog.Log.Information("[Purchase] Id={Id} Type={Type} Note={Note} IsTopup={IsTopup}", p.Id, p.Type, p.Note, p.IsOperatorTopup);'

count = c.count(old)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\PurchaseService.cs', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
