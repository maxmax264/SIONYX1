content = open(r'.\src\SionyxKiosk\App.xaml.cs', encoding='utf-8').read()
old = "                    var phone = AppConstants.SupportPhone;"
new = "                    var phone = \"0775022924\";"
count = content.count(old)
print(f"match: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\App.xaml.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
