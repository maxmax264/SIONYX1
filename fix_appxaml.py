content = open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml', encoding='utf-8').read()

old = '''            <BooleanToVisibilityConverter x:Key="BoolToVis" />'''

new = '''            <BooleanToVisibilityConverter x:Key="BoolToVis" />
            <infra:InverseBoolToVisibilityConverter x:Key="InverseBoolToVis" />'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
