content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml', encoding='utf-8').read()

old = '''<Grid Margin="0,0,0,14">
                                                <!-- הודעת פיקוח/מנהל - משמאל, אפור -->
                                                <Border CornerRadius="12" Padding="14,10" MaxWidth="340"
                                                        HorizontalAlignment="Left">
                                                    <Border.Style>
                                                        <Style TargetType="Border">
                                                            <Setter Property="Background" Value="#F1F5F9"/>
                                                            <Setter Property="Visibility" Value="Collapsed"/>
                                                            <Style.Triggers>
                                                                <DataTrigger Binding="{Binding FromSupervisor}" Value="True">
                                                                    <Setter Property="Visibility" Value="Visible"/>
                                                                </DataTrigger>
                                                            </Style.Triggers>
                                                        </Style>
                                                    </Border.Style>
                                                    <StackPanel>
                                                        <TextBlock Text="{Binding SenderName}"
                                                                   FontSize="12" FontWeight="Bold"
                                                                   Foreground="#6366F1" Margin="0,0,0,4"
                                                                   FlowDirection="RightToLeft"/>
                                                        <TextBlock Text="{Binding DisplayBody}"
                                                                   TextWrapping="Wrap" FontSize="14"
                                                                   LineHeight="22" Foreground="#1E293B"
                                                                   FlowDirection="RightToLeft"/>
                                                        <TextBlock Text="{Binding DisplayTime}"
                                                                   FontSize="11" Foreground="#94A3B8"
                                                                   HorizontalAlignment="Left" Margin="0,4,0,0"/>
                                                    </StackPanel>
                                                </Border>
                                                <!-- הודעת משתמש - מימין, כחול -->
                                                <Border CornerRadius="12" Padding="14,10" MaxWidth="340"
                                                        HorizontalAlignment="Right">
                                                    <Border.Style>
                                                        <Style TargetType="Border">
                                                            <Setter Property="Visibility" Value="Collapsed"/>
                                                            <Style.Triggers>
                                                                <DataTrigger Binding="{Binding FromSupervisor}" Value="False">
                                                                    <Setter Property="Visibility" Value="Visible"/>
                                                                </DataTrigger>
                                                            </Style.Triggers>
                                                        </Style>
                                                    </Border.Style>
                                                    <Border.Background>
                                                        <LinearGradientBrush StartPoint="0,0" EndPoint="1,1">
                                                            <GradientStop Color="#6366F1" Offset="0"/>
                                                            <GradientStop Color="#8B5CF6" Offset="1"/>
                                                        </LinearGradientBrush>
                                                    </Border.Background>
                                                    <StackPanel>
                                                        <TextBlock Text="אתה" FontSize="12" FontWeight="Bold"
                                                                   Foreground="#C7D2FE" Margin="0,0,0,4"
                                                                   HorizontalAlignment="Right"/>
                                                        <TextBlock Text="{Binding DisplayBody}"
                                                                   TextWrapping="Wrap" FontSize="14"
                                                                   LineHeight="22" Foreground="White"
                                                                   FlowDirection="RightToLeft"/>
                                                        <StackPanel Orientation="Horizontal" HorizontalAlignment="Right"
                                                                    Margin="0,4,0,0">
                                                            <Button Content="מחק" Margin="0,0,8,0" Padding="8,2"
                                                                    FontSize="11" Cursor="Hand"
                                                                    Background="#EF4444" Foreground="White"
                                                                    BorderThickness="0" Tag="{Binding Id}"
                                                                    Click="DeleteMessage_Click"/>
                                                            <TextBlock Text="{Binding DisplayTime}"
                                                                       FontSize="11" Foreground="#C7D2FE"
                                                                       VerticalAlignment="Center"/>
                                                        </StackPanel>
                                                    </StackPanel>
                                                </Border>
                                            </Grid>'''

new = '''<ContentControl Margin="0,0,0,14">
                                                <ContentControl.Style>
                                                    <Style TargetType="ContentControl">
                                                        <Style.Triggers>
                                                            <!-- הודעת מנהל/פיקוח - משמאל, אפור -->
                                                            <DataTrigger Binding="{Binding FromSupervisor}" Value="True">
                                                                <Setter Property="Content">
                                                                    <Setter.Value>
                                                                        <Border CornerRadius="12" Padding="14,10"
                                                                                MaxWidth="340" HorizontalAlignment="Left"
                                                                                Background="#F1F5F9">
                                                                            <StackPanel>
                                                                                <TextBlock Text="{Binding SenderName}"
                                                                                           FontSize="12" FontWeight="Bold"
                                                                                           Foreground="#6366F1" Margin="0,0,0,4"
                                                                                           TextAlignment="Right"/>
                                                                                <TextBlock Text="{Binding DisplayBody}"
                                                                                           TextWrapping="Wrap" FontSize="14"
                                                                                           LineHeight="22" Foreground="#1E293B"
                                                                                           TextAlignment="Right"/>
                                                                                <TextBlock Text="{Binding DisplayTime}"
                                                                                           FontSize="11" Foreground="#94A3B8"
                                                                                           HorizontalAlignment="Left"
                                                                                           Margin="0,4,0,0"/>
                                                                            </StackPanel>
                                                                        </Border>
                                                                    </Setter.Value>
                                                                </Setter>
                                                            </DataTrigger>
                                                            <!-- הודעת משתמש - מימין, כחול -->
                                                            <DataTrigger Binding="{Binding FromSupervisor}" Value="False">
                                                                <Setter Property="Content">
                                                                    <Setter.Value>
                                                                        <Border CornerRadius="12" Padding="14,10"
                                                                                MaxWidth="340" HorizontalAlignment="Right">
                                                                            <Border.Background>
                                                                                <LinearGradientBrush StartPoint="0,0" EndPoint="1,1">
                                                                                    <GradientStop Color="#6366F1" Offset="0"/>
                                                                                    <GradientStop Color="#8B5CF6" Offset="1"/>
                                                                                </LinearGradientBrush>
                                                                            </Border.Background>
                                                                            <StackPanel>
                                                                                <TextBlock Text="אתה"
                                                                                           FontSize="12" FontWeight="Bold"
                                                                                           Foreground="#C7D2FE" Margin="0,0,0,4"
                                                                                           HorizontalAlignment="Right"/>
                                                                                <TextBlock Text="{Binding DisplayBody}"
                                                                                           TextWrapping="Wrap" FontSize="14"
                                                                                           LineHeight="22" Foreground="White"
                                                                                           TextAlignment="Right"/>
                                                                                <StackPanel Orientation="Horizontal"
                                                                                            HorizontalAlignment="Right"
                                                                                            Margin="0,4,0,0">
                                                                                    <Button Content="מחק" Margin="0,0,8,0"
                                                                                            Padding="8,2" FontSize="11"
                                                                                            Cursor="Hand"
                                                                                            Background="#EF4444"
                                                                                            Foreground="White"
                                                                                            BorderThickness="0"
                                                                                            Tag="{Binding Id}"
                                                                                            Click="DeleteMessage_Click"/>
                                                                                    <TextBlock Text="{Binding DisplayTime}"
                                                                                               FontSize="11" Foreground="#C7D2FE"
                                                                                               VerticalAlignment="Center"/>
                                                                                </StackPanel>
                                                                            </StackPanel>
                                                                        </Border>
                                                                    </Setter.Value>
                                                                </Setter>
                                                            </DataTrigger>
                                                        </Style.Triggers>
                                                    </Style>
                                                </ContentControl.Style>
                                            </ContentControl>'''

count = content.count(old)
print(f"Found: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml', 'w', encoding='utf-8').write(content)
    print('Done')
else:
    print('NOT FOUND')
