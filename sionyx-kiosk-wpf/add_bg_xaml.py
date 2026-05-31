f = open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', encoding='utf-8')
c = f.read()
f.close()

old = '    <Grid Background="{StaticResource AuthPageBg}">'
new = '''    <Grid Background="{StaticResource AuthPageBg}">
        <!-- Background image - shown only when kioskBackgroundEnabled=true -->
        <Image x:Name="BgImage"
               Source="{Binding BackgroundImageUrl}"
               Stretch="UniformToFill"
               Visibility="{Binding HasBackgroundImage, Converter={StaticResource BoolToVis}}"
               Opacity="0.55" Panel.ZIndex="0" />'''

assert c.count(old) == 1
c = c.replace(old, new, 1)
open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', 'w', encoding='utf-8').write(c)
print("XAML OK")
