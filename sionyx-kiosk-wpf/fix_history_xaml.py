content = open(r'.\src\SionyxKiosk\Views\Pages\HistoryPage.xaml', encoding='utf-8').read()

old = "        </ScrollViewer>\n    </Grid>\n</Page>"

new = """        </ScrollViewer>

        <!-- Tab: Sessions -->
        <ScrollViewer Grid.Row="3" Visibility="{Binding IsSessionsTabVisible, FallbackValue=Collapsed}">
            <StackPanel Margin="0,0,0,32">
                <controls:EmptyState Message="אין היסטוריית שימוש" 
                    Visibility="{Binding SessionLogs.Count, Converter={StaticResource ZeroToVisConverter}, FallbackValue=Visible}" />
                <ItemsControl ItemsSource="{Binding SessionLogs}">
                    <ItemsControl.ItemTemplate>
                        <DataTemplate>
                            <Border Background="White" CornerRadius="12" Margin="0,0,0,10"
                                    BorderBrush="#E5E7EB" BorderThickness="1" Padding="16">
                                <Grid>
                                    <Grid.ColumnDefinitions>
                                        <ColumnDefinition Width="*"/>
                                        <ColumnDefinition Width="Auto"/>
                                    </Grid.ColumnDefinitions>
                                    <StackPanel Grid.Column="0">
                                        <TextBlock Text="{Binding EndTimeDisplay}" FontWeight="SemiBold" FontSize="14" Foreground="#1F2937"/>
                                        <TextBlock Text="{Binding ComputerName}" FontSize="12" Foreground="#6B7280" Margin="0,2,0,0"/>
                                    </StackPanel>
                                    <StackPanel Grid.Column="1" HorizontalAlignment="Right">
                                        <TextBlock Text="{Binding UsedMinutesDisplay}" FontWeight="Bold" FontSize="14" Foreground="#667EEA" HorizontalAlignment="Right"/>
                                        <TextBlock Text="{Binding ReasonDisplay}" FontSize="11" Foreground="#9CA3AF" HorizontalAlignment="Right" Margin="0,2,0,0"/>
                                    </StackPanel>
                                </Grid>
                            </Border>
                        </DataTemplate>
                    </ItemsControl.ItemTemplate>
                </ItemsControl>
            </StackPanel>
        </ScrollViewer>

        <!-- Tab: Prints -->
        <ScrollViewer Grid.Row="3" Visibility="{Binding IsPrintsTabVisible, FallbackValue=Collapsed}">
            <StackPanel Margin="0,0,0,32">
                <controls:EmptyState Message="אין היסטוריית הדפסות"
                    Visibility="{Binding PrintLogs.Count, Converter={StaticResource ZeroToVisConverter}, FallbackValue=Visible}" />
                <ItemsControl ItemsSource="{Binding PrintLogs}">
                    <ItemsControl.ItemTemplate>
                        <DataTemplate>
                            <Border Background="White" CornerRadius="12" Margin="0,0,0,10"
                                    BorderBrush="#E5E7EB" BorderThickness="1" Padding="16">
                                <Grid>
                                    <Grid.ColumnDefinitions>
                                        <ColumnDefinition Width="*"/>
                                        <ColumnDefinition Width="Auto"/>
                                    </Grid.ColumnDefinitions>
                                    <StackPanel Grid.Column="0">
                                        <TextBlock Text="{Binding DocName}" FontWeight="SemiBold" FontSize="14" Foreground="#1F2937" TextTrimming="CharacterEllipsis"/>
                                        <TextBlock Text="{Binding TimestampDisplay}" FontSize="12" Foreground="#6B7280" Margin="0,2,0,0"/>
                                        <TextBlock Text="{Binding PrinterName}" FontSize="11" Foreground="#9CA3AF" Margin="0,2,0,0"/>
                                    </StackPanel>
                                    <StackPanel Grid.Column="1" HorizontalAlignment="Right">
                                        <TextBlock Text="{Binding CostDisplay}" FontWeight="Bold" FontSize="14" Foreground="#10B981" HorizontalAlignment="Right"/>
                                        <TextBlock FontSize="12" Foreground="#6B7280" HorizontalAlignment="Right" Margin="0,2,0,0">
                                            <Run Text="{Binding Pages}"/><Run Text=" עמ'"/>
                                        </TextBlock>
                                    </StackPanel>
                                </Grid>
                            </Border>
                        </DataTemplate>
                    </ItemsControl.ItemTemplate>
                </ItemsControl>
            </StackPanel>
        </ScrollViewer>

    </Grid>
</Page>"""

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Pages\HistoryPage.xaml', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
