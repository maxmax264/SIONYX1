f = open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8')
c = f.read()
f.close()
import re
matches = re.findall(r'FormX|FormY|FormWidth', c)
idx = c.find('[ObservableProperty]')
# מצא את כל ה-ObservableProperty עם Form
for m in re.finditer(r'\[ObservableProperty\][^\[]*?(FormX|FormY|FormWidth)[^;]*;', c, re.DOTALL):
    print(m.group())
    print('---')
