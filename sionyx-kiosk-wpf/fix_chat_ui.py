content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml', encoding='utf-8').read()

old = '''<Border Margin="0,0,0,14" CornerRadius="12"
                                                    Background="#F1F5F9" Padding="18,14">
                                                <Grid>
                                                    <Grid.ColumnDefinitions>
                                                        <ColumnDefinition Width="Auto" />
                                                        <ColumnDefinition Width="*" />
                                                    </Grid.ColumnDefinitions>
                                                    <Border Grid.Column="0" Width="40" Height="40"
                                                            CornerRadius="20" Margin="0,0,12,0"
                                                            VerticalAlignment="Top">
                                                        <Border.Background>
                                                            <LinearGradientBrush StartPoint="0,0" EndPoint="1,1">
                                                                <GradientStop Color="#6366F1" Offset="0" />
                                                                <GradientStop Color="#8B5CF6" Offset="1" />
                                                            </LinearGradientBrush>
                                                        </Border.Background>
                                                        <TextBlock Text="&#xE77B;" FontFamily="Segoe MDL2 Assets"
                                                                   FontSize="16" Foreground="White"
                                                                   HorizontalAlignment="Center" VerticalAlignment="Center" />
                                                    </Border>
                                                    <StackPanel Grid.Column="1">
                                                        <Grid Margin="0,0,0,6">
                                                            <Grid.ColumnDefinitions>
                                                                <ColumnDefinition Width="*" />
                                                                <ColumnDefinition Width="Auto" />
                                                            </Grid.ColumnDefinitions>
                                                            <TextBlock Grid.Column="0"
                                                                       Text="{Binding SenderName}"
                                                                       FontSize="13" FontWeight="Bold"
                                                                       Foreground="#4338CA" />
                                                            <TextBlock Grid.Column="1"
                                                                       Text="{Binding DisplayTime}"
                                                                       FontSize="11" Foreground="{StaticResource TextMutedBrush}"
                                                                       VerticalAlignment="Center" />
                                                        </Grid>
                                                        <TextBlock Text="{Binding DisplayBody}"
                                                                   TextWrapping="Wrap" FontSize="14"
                                                                   LineHeight="22"
                                                                   Foreground="{StaticResource TextPrimaryBrush}" />
                                                        <Button Content="מחק" HorizontalAlignment="Left"
                                                                Margin="0,8,0,0" Padding="10,4"
                                                                FontSize="12" Cursor="Hand"
                                                                Background="#FEE2E2" Foreground="#DC2626"
                                                                BorderThickness="0" Tag="{Binding Id}"
                                                                Click="DeleteMessage_Click" />
                                                    </StackPanel>
                                                </Grid>
                                            </Border>'''

new = '''<Grid Margin="0,0,0,14">
                                                <Grid.Style>
                                                    <Style TargetType="Grid">
                                                        <Setter Property="FlowDirection" Value="RightToLeft"/>
                                                    </Style>
                                                </Grid.Style>
                                                <!-- הודעת פיקוח/מנהל - משמאל -->
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
                                                    <StackPanel FlowDirection="RightToLeft">
                                                        <TextBlock Text="{Binding SenderName}"
                                                                   FontSize="12" FontWeight="Bold"
                                                                   Foreground="#6366F1" Margin="0,0,0,4"/>
                                                        <TextBlock Text="{Binding DisplayBody}"
                                                                   TextWrapping="Wrap" FontSize="14"
                                                                   LineHeight="22"
                                                                   Foreground="#1E293B"/>
                                                        <TextBlock Text="{Binding DisplayTime}"
                                                                   FontSize="11" Foreground="#94A3B8"
                                                                   HorizontalAlignment="Left" Margin="0,4,0,0"/>
                                                    </StackPanel>
                                                </Border>
                                                <!-- הודעת משתמש - מימין -->
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
                                                    <StackPanel FlowDirection="RightToLeft">
                                                        <TextBlock Text="{Binding DisplayBody}"
                                                                   TextWrapping="Wrap" FontSize="14"
                                                                   LineHeight="22" Foreground="White"/>
                                                        <StackPanel Orientation="Horizontal" HorizontalAlignment="Left"
                                                                    Margin="0,4,0,0">
                                                            <TextBlock Text="{Binding DisplayTime}"
                                                                       FontSize="11" Foreground="#C7D2FE"/>
                                                            <Button Content="מחק" Margin="8,0,0,0" Padding="8,2"
                                                                    FontSize="11" Cursor="Hand"
                                                                    Background="#EF4444" Foreground="White"
                                                                    BorderThickness="0" Tag="{Binding Id}"
                                                                    Click="DeleteMessage_Click"/>
                                                        </StackPanel>
                                                    </StackPanel>
                                                </Border>
                                            </Grid>'''

count = content.count(old)
print(f"Found: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml', 'w', encoding='utf-8').write(content)
    print('Done')
else:
    print('NOT FOUND')
