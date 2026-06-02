content = open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8').read()

old = "                            bmp.EndInit();\n                            BackgroundImageSource = bmp;"
new = "                            bmp.EndInit();\n                            bmp.Freeze();\n                            BackgroundImageSource = bmp;"

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\AuthViewModel.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    old2 = "                            bmp.EndInit();\r\n                            BackgroundImageSource = bmp;"
    new2 = "                            bmp.EndInit();\r\n                            bmp.Freeze();\r\n                            BackgroundImageSource = bmp;"
    count2 = content.count(old2)
    print(f"Found2 {count2} matches")
    if count2 == 1:
        content = content.replace(old2, new2, 1)
        open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\AuthViewModel.cs', 'w', encoding='utf-8').write(content)
        print('OK')
    else:
        print('NOT FOUND')
