content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml', encoding='utf-8').read()

# תיקון מנהל — רקע אפור בולט יותר
old = '''                                                            <Setter Property="Visibility" Value="Collapsed"/>
                                                            <Style.Triggers>
                                                                <DataTrigger Binding="{Binding IsUserReply}" Value="False">
                                                                    <Setter Property="Visibility" Value="Visible"/>
                                                                </DataTrigger>
                                                            </Style.Triggers>
                                                        </Style>
                                                    </Border.Style>
                                                    <StackPanel>
                                                        <TextBlock Text="{Binding SenderName}"
                                                                   FontSize="11" FontWeight="Bold"
                                                                   Foreground="#6366F1" Margin="0,0,0,3"/>'''
new = '''                                                            <Setter Property="Visibility" Value="Collapsed"/>
                                                            <Setter Property="Background" Value="#E8EAF6"/>
                                                            <Setter Property="BorderBrush" Value="#6366F1"/>
                                                            <Setter Property="BorderThickness" Value="1.5"/>
                                                            <Style.Triggers>
                                                                <DataTrigger Binding="{Binding IsUserReply}" Value="False">
                                                                    <Setter Property="Visibility" Value="Visible"/>
                                                                </DataTrigger>
                                                            </Style.Triggers>
                                                        </Style>
                                                    </Border.Style>
                                                    <StackPanel>
                                                        <TextBlock Text="{Binding SenderName}"
                                                                   FontSize="11" FontWeight="Bold"
                                                                   Foreground="#6366F1" Margin="0,0,0,3"/>'''
count = content.count(old)
print(f"Fix admin: Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    print("Fix admin: OK")
else:
    print("Fix admin: NOT FOUND")

# תיקון פיקוח — רקע ירוק בולט יותר
old2 = '''                                                            <Setter Property="Visibility" Value="Collapsed"/>
                                                            <Setter Property="Background" Value="#F0FDF4"/>
                                                            <Style.Triggers>
                                                                <DataTrigger Binding="{Binding IsUserReply}" Value="False">
                                                                    <Setter Property="Visibility" Value="Visible"/>
                                                                </DataTrigger>'''
new2 = '''                                                            <Setter Property="Visibility" Value="Collapsed"/>
                                                            <Setter Property="Background" Value="#D1FAE5"/>
                                                            <Setter Property="BorderBrush" Value="#059669"/>
                                                            <Setter Property="BorderThickness" Value="1.5"/>
                                                            <Style.Triggers>
                                                                <DataTrigger Binding="{Binding IsUserReply}" Value="False">
                                                                    <Setter Property="Visibility" Value="Visible"/>
                                                                </DataTrigger>'''
count2 = content.count(old2)
print(f"Fix supervisor: Found {count2} matches")
if count2 == 1:
    content = content.replace(old2, new2, 1)
    print("Fix supervisor: OK")
else:
    print("Fix supervisor: NOT FOUND")

open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml', 'w', encoding='utf-8').write(content)
print('Done')
