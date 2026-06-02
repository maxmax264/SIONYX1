f = open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8')
c = f.read()
f.close()
for i, line in enumerate(c.split('\n')):
    if any(x in line for x in ['formX', 'formY', 'formWidth', 'FormX', 'FormY', 'FormWidth']):
        print(f'{i+1}: {line.strip()}')
