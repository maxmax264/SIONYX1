f = open(r'.\src\SionyxKiosk\Models\Package.cs', encoding='utf-8')
c = f.read()
f.close()

old = '    public string UpdatedAt { get; set; } = "";\n}'
new = '    public string UpdatedAt { get; set; } = "";\n    public string Type { get; set; } = "";\n    public string Note { get; set; } = "";\n    public bool IsOperatorTopup => Type == "admin_charge" || Note == "טעינת מפעיל";\n}'

count = c.count(old)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Models\Package.cs', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
