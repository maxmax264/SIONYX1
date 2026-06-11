content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml', encoding='utf-8').read()
old = """                            <!-- List -->
                            <ScrollViewer x:Name="SupervisorScroll" VerticalScrollBarVisibility="Auto"
                                          Padding="20,16" Visibility="Collapsed">
                                <ItemsControl x:Name="SupervisorMessagesList">
                                    <ItemsControl.ItemTemplate>
                                        <DataTemplate>
                                            <Border Margin="0,0,0,14" CornerRadius="12"
                                                    Background="#F0FDF4" Padding="18,14">
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
                                                                <GradientStop Color="#059669" Offset="0" />
                                                                <GradientStop Color="#10B981" Offset="1" />
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
                                                                       Foreground="#059669" />
                                                            <TextBlock Grid.Column="1"
                                                                       Text="{Binding DisplayTime}"
                                                                       FontSize="11" Foreground="{StaticResource TextMutedBrush}"
                                                                       VerticalAlignment="Center" />
                                                        </Grid>
                                                        <TextBlock Text="{Binding DisplayBody}"
                                                                   TextWrapping="Wrap" FontSize="14"
                                                                   LineHeight="22"
                                                                   Foreground="{StaticResource TextPrimaryBrush}" />
                                                    </StackPanel>
                                                </Grid>
                                            </Border>
                                        </DataTemplate>
                                    </ItemsControl.ItemTemplate>
                                </ItemsControl>
                            </ScrollViewer>"""
new = """                            <!-- List -->
                            <ScrollViewer x:Name="SupervisorScroll" VerticalScrollBarVisibility="Auto"
                                          Padding="20,16" Visibility="Collapsed">
                                <ItemsControl x:Name="SupervisorMessagesList">
                                    <ItemsControl.ItemTemplate>
                                        <DataTemplate>
                                            <Border Margin="0,0,0,10" HorizontalAlignment="{Binding BubbleAlign}"
                                                    MaxWidth="320" CornerRadius="14"
                                                    Background="{Binding BubbleBg}" Padding="14,10">
                                                <StackPanel>
                                                    <Grid Margin="0,0,0,4">
                                                        <Grid.ColumnDefinitions>
                                                            <ColumnDefinition Width="*" />
                                                            <ColumnDefinition Width="Auto" />
                                                        </Grid.ColumnDefinitions>
                                                        <TextBlock Grid.Column="0"
                                                                   Text="{Binding SenderLabel}"
                                                                   FontSize="12" FontWeight="Bold"
                                                                   Foreground="{Binding BubbleFg}" />
                                                        <TextBlock Grid.Column="1"
                                                                   Text="{Binding DisplayTime}"
                                                                   FontSize="11" Foreground="{StaticResource TextMutedBrush}"
                                                                   VerticalAlignment="Center" Margin="8,0,0,0" />
                                                    </Grid>
                                                    <TextBlock Text="{Binding DisplayBody}"
                                                               TextWrapping="Wrap" FontSize="14"
                                                               LineHeight="22"
                                                               Foreground="{StaticResource TextPrimaryBrush}" />
                                                </StackPanel>
                                            </Border>
                                        </DataTemplate>
                                    </ItemsControl.ItemTemplate>
                                </ItemsControl>
                            </ScrollViewer>"""
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
