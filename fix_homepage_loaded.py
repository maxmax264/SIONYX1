content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Pages\HomePage.xaml.cs', encoding='utf-8').read()
old = '''        Unloaded += OnPageUnloaded;'''
new = '''        Loaded += OnPageLoaded;
        Unloaded += OnPageUnloaded;'''
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Pages\HomePage.xaml.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
