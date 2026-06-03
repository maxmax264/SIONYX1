f = open(r'.\src\SionyxKiosk\Models\Package.cs', encoding='utf-8')
c = f.read()
f.close()

old = '    public bool IsOperatorTopup => Type == "admin_charge" || Note == "טעינת מפעיל";'
new = '    public bool IsOperatorTopup => Type == "admin_charge" || Note == "טעינת מפעיל";\n    public int TimeSeconds { get; set; }\n    public int TimeMinutes => TimeSeconds != 0 ? TimeSeconds / 60 : Minutes;'

count = c.count(old)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Models\Package.cs', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
