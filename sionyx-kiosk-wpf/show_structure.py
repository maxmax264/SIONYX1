f = open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', encoding='utf-8')
c = f.read()
f.close()
for i, line in enumerate(c.split('\n')):
    if any(x in line for x in ['BrandOverlay', 'CleanMode', 'StackPanel', 'Grid', 'Canvas', 'FormBox']):
        print(f'{i+1}: {line}')
