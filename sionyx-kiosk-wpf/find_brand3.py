f=open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', encoding='utf-8')
c=f.read()
f.close()
idx=c.find('Canvas.Left="-3"')
if idx == -1:
    idx=c.find('Canvas.Left="0"')
print(c[idx:idx+2000])
