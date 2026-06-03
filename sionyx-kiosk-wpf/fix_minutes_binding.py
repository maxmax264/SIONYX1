f = open(r'.\src\SionyxKiosk\Views\Pages\HistoryPage.xaml', encoding='utf-8')
c = f.read()
f.close()

old = '                                Minutes="{Binding Minutes}"'
new = '                                Minutes="{Binding TimeMinutes}"'

count = c.count(old)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Pages\HistoryPage.xaml', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
