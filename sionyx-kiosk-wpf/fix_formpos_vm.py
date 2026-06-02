f = open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8')
c = f.read()
f.close()

# הוסף properties
old = '[ObservableProperty] private bool _cleanMode = false;'
new = '[ObservableProperty] private bool _cleanMode = false;\n    [ObservableProperty] private double _formX = 50;\n    [ObservableProperty] private double _formY = 50;\n    [ObservableProperty] private double _formWidth = 340;'
count = c.count(old)
print(f'Properties match: {count}')
if count == 1:
    c = c.replace(old, new, 1)

# הוסף קריאה מ-Firebase
old2 = 'if (d.TryGetProperty("cleanMode", out var cm)) {'
new2 = 'if (d.TryGetProperty("formX", out var fx)) FormX = fx.GetDouble();\n                if (d.TryGetProperty("formY", out var fy)) FormY = fy.GetDouble();\n                if (d.TryGetProperty("formWidth", out var fw)) FormWidth = fw.GetDouble();\n                if (d.TryGetProperty("cleanMode", out var cm)) {'
count2 = c.count(old2)
print(f'Firebase match: {count2}')
if count2 == 1:
    c = c.replace(old2, new2, 1)

if count == 1 and count2 == 1:
    open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
