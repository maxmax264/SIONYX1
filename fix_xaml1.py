content = open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', encoding='utf-8').read()

old = '''                <Border x:Name="BrandOverlay" Canvas.Left="-3" Canvas.Top="-3"
                        Width="503" Height="706"
                        CornerRadius="20"
                        Background="{StaticResource AuthGradient}">
                    <StackPanel VerticalAlignment="Center" HorizontalAlignment="Center" Margin="48">
                        <TextBlock Text="SIONYX" FontSize="46" FontWeight="ExtraBold"
                                   Foreground="White" HorizontalAlignment="Center" Margin="0,0,0,16" />
                        <TextBlock x:Name="BrandSubtitle" Text="ניהול מחשבים חכם" FontSize="18"
                                   Foreground="#DDFFFFFF" HorizontalAlignment="Center"
                                   TextAlignment="Center" FontWeight="Light" />
                    </StackPanel>
                </Border>'''

new = '''                <Border x:Name="BrandOverlay" Canvas.Left="-3" Canvas.Top="-3"
                        Width="503" Height="706"
                        CornerRadius="20"
                        Background="{Binding OverlayGradient}">
                    <StackPanel VerticalAlignment="Center" HorizontalAlignment="Center" Margin="48"
                                Visibility="{Binding CleanMode, Converter={StaticResource InverseBoolToVis}}">
                        <TextBlock Text="SIONYX" FontSize="46" FontWeight="ExtraBold"
                                   Foreground="White" HorizontalAlignment="Center" Margin="0,0,0,16" />
                        <TextBlock x:Name="BrandSubtitleBlock" Text="{Binding BrandSubtitle}" FontSize="18"
                                   Foreground="#DDFFFFFF" HorizontalAlignment="Center"
                                   TextAlignment="Center" FontWeight="Light" />
                    </StackPanel>
                </Border>'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
