content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml', encoding='utf-8').read()
old = """                                                        <TextBlock Text="{Binding DisplayBody}"
                                                                   TextWrapping="Wrap" FontSize="14"
                                                                   LineHeight="22"
                                                                   Foreground="{StaticResource TextPrimaryBrush}" />
                                                    </StackPanel>
                                                </Grid>
                                            </Border>
                                        </DataTemplate>
                                    </ItemsControl.ItemTemplat"""

new = """                                                        <TextBlock Text="{Binding DisplayBody}"
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
                                            </Border>
                                        </DataTemplate>
                                    </ItemsControl.ItemTemplat"""

count = content.count(old)
print(f"Found: {count}")
content = content.replace(old, new)
open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml', 'w', encoding='utf-8').write(content)
print('Done - replaced all')
