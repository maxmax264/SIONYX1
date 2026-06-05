content = open(r'.\src\SionyxKiosk\Views\Pages\ProfilePage.xaml', encoding='utf-8').read()
old = '      Title="פרופיל" FlowDirection="RightToLeft">'
new = '''      Title="פרופיל" FlowDirection="RightToLeft">
    <Page.Resources>
        <BooleanToVisibilityConverter x:Key="BoolToVis" />
    </Page.Resources>'''
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Pages\ProfilePage.xaml', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
