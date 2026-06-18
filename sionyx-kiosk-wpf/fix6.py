content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml', encoding='utf-8').read()

old = '''                                                <Border CornerRadius="14" Padding="12,10"
                                                        MaxWidth="280" HorizontalAlignment="Left"
                                                        Background="#F0FDF4" Margin="0,0,80,0"
                                                        FlowDirection="LeftToRight">
                                                    <Border.Style>
                                                        <Style TargetType="Border">
                                                            <Setter Property="Visibility" Value="Collapsed"/>
                                                            <Style.Triggers>'''
new = '''                                                <Border CornerRadius="14" Padding="12,10"
                                                        MaxWidth="280" HorizontalAlignment="Left"
                                                        Margin="0,0,80,0"
                                                        FlowDirection="LeftToRight">
                                                    <Border.Style>
                                                        <Style TargetType="Border">
                                                            <Setter Property="Visibility" Value="Collapsed"/>
                                                            <Setter Property="Background" Value="#F0FDF4"/>
                                                            <Style.Triggers>'''
count = content.count(old)
print(f"Fix: Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    print("Fix: OK")
else:
    print("Fix: NOT FOUND")

open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml', 'w', encoding='utf-8').write(content)
print('Done')
