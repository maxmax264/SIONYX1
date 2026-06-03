f = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', encoding='utf-8')
c = f.read()
f.close()
old = '''                        <DataTrigger Binding="{Binding CleanMode}" Value="True">
                            <Setter Property="HorizontalAlignment" Value="Left"/>
                            <Setter Property="VerticalAlignment" Value="Top"/>
                            <Setter Property="Margin" Value="{Binding FormMargin}"/>
                        </DataTrigger>'''
new = '''                        <DataTrigger Binding="{Binding CleanMode}" Value="True">
                            <Setter Property="HorizontalAlignment" Value="Center"/>
                            <Setter Property="VerticalAlignment" Value="Center"/>
                        </DataTrigger>'''
count = c.count(old)
print(f"Found {count} matches")
if count == 1:
    c = c.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', 'w', encoding='utf-8').write(c)
    print("OK")
else:
    print("NOT FOUND")
