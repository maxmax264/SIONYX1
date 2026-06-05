import re, sys

path = r'.\src\SionyxKiosk\Views\Pages\ProfilePage.xaml'
content = open(path, encoding='utf-8').read()

# החלף את בלוק הודעת הסטטוס
old = '''                <!-- הודעת סטטוס -->
                <Border Padding="16,12" CornerRadius="{StaticResource RadiusLg}" Margin="0,0,0,20">
                    <Border.Style>
                        <Style TargetType="Border">
                            <Setter Property="Visibility" Value="Collapsed" />
                            <Style.Triggers>
                                <DataTrigger Binding="{Binding StatusMessage}" Value="">
                                    <Setter Property="Visibility" Value="Collapsed" />
                                </DataTrigger>
                            </Style.Triggers>
                        </Style>
                    </Border.Style>
                    <Border.Background>
                        <SolidColorBrush Color="#F0FDF4" />
                    </Border.Background>
                    <TextBlock Text="{Binding StatusMessage}" FontSize="14" FontWeight="SemiBold"
                               Foreground="{StaticResource SuccessBrush}" TextWrapping="Wrap" />
                </Border>'''

new = '''                <!-- הודעת סטטוס -->
                <Border x:Name="StatusBorder" Padding="16,12" CornerRadius="{StaticResource RadiusLg}"
                        Margin="0,0,0,20" Visibility="{Binding ShowStatus, Converter={StaticResource BoolToVis}}">
                    <Border.Background>
                        <SolidColorBrush Color="#F0FDF4" />
                    </Border.Background>
                    <TextBlock Text="{Binding StatusMessage}" FontSize="14" FontWeight="SemiBold"
                               Foreground="{StaticResource SuccessBrush}" TextWrapping="Wrap" />
                </Border>'''

content = content.replace(old, new)
open(path, 'w', encoding='utf-8').write(content)
print('XAML OK')
