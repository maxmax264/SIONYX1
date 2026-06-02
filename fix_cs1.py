content = open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Windows\AuthWindow.xaml.cs', encoding='utf-8').read()

old1 = 'BrandSubtitle.Text = "הצטרף אלינו היום";'
new1 = 'BrandSubtitleBlock.Text = "הצטרף אלינו היום";'

old2 = 'BrandSubtitle.Text = "ניהול מחשבים חכם";'
new2 = 'BrandSubtitleBlock.Text = "ניהול מחשבים חכם";'

c1 = content.count(old1)
c2 = content.count(old2)
print(f"Match1={c1} Match2={c2}")
if c1 == 1 and c2 == 1:
    content = content.replace(old1, new1, 1)
    content = content.replace(old2, new2, 1)
    open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Windows\AuthWindow.xaml.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
