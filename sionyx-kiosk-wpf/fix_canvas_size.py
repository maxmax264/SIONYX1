f = open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', encoding='utf-8')
c = f.read()
f.close()

old = '''        <Canvas x:Name="FormCanvas" Panel.ZIndex="1"
                Visibility="{Binding CleanMode, Converter={StaticResource BoolToVis}}">'''

new = '''        <Canvas x:Name="FormCanvas" Panel.ZIndex="1"
                Width="{Binding ActualWidth, RelativeSource={RelativeSource AncestorType=Window}}"
                Height="{Binding ActualHeight, RelativeSource={RelativeSource AncestorType=Window}}"
                Visibility="{Binding CleanMode, Converter={StaticResource BoolToVis}}">'''

count = c.count(old)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
