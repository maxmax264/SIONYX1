f = open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8')
c = f.read()
f.close()
idx = c.find('public void Reset')
if idx == -1:
    idx = c.find('public void Clear')
if idx == -1:
    print('No reset found - need to add')
    # מצא את הfields
    import re
    for m in re.finditer(r'\[ObservableProperty\].*?private string _(phone|password|firstName|lastName|email)', c):
        print(m.group())
else:
    print(c[idx:idx+200])
