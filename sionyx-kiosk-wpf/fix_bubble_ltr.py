path = r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml'
content = open(path, encoding='utf-8').read()

old = '<Grid Margin="0,0,0,10">'
new = '<Grid Margin="0,0,0,10" FlowDirection="LeftToRight">'

count = content.count(old)
print(f"Found {count} matches")
content = content.replace(old, new)
open(path, 'w', encoding='utf-8').write(content)
print("OK")
