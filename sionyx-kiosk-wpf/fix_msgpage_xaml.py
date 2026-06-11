content = """<Page x:Class="SionyxKiosk.Views.Pages.MessagesPage"
      xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
      xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
      Title="הודעות" FlowDirection="RightToLeft">

    <Page.Resources>
        <BooleanToVisibilityConverter x:Key="BoolToVis" />
    </Page.Resources>

    <Grid>
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto" />
            <RowDefinition Height="*" />
        </Grid.RowDefinitions>

        <!-- Header -->
        <Border Grid.Row="0" Margin="0,0,0,20">
            <StackPanel>
                <TextBlock Text="הודעות" FontSize="24" FontWeight="Bold"
                           Foreground="{StaticResource TextPrimaryBrush}" Margin="0,0,0,6" />
                <TextBlock Text="הודעות ממנהל החנות ומהפיקוח" FontSize="14"
                           Foreground="{StaticResource TextMutedBrush}" />
            </StackPanel>
        </Border>

        <!-- Tab Control -->
        <TabControl Grid.Row="1" x:Name="MainTabControl"
                    Background="Transparent" BorderThickness="0">
            <TabControl.Resources>
                <Style TargetType="TabItem">
                    <Setter Property="FontSize" Value="14" />
                    <Setter Property="Padding" Value="16,10" />
                    <Setter Property="Foreground" Value="{StaticResource TextMutedBrush}" />
                    <Setter Property="Background" Value="Transparent" />
                    <Setter Property="BorderThickness" Value="0" />
                    <Setter Property="Template">
                        <Setter.Value>
                            <ControlTemplate TargetType="TabItem">
                                <Border x:Name="TabBorder" Padding="16,10" Margin="0,0,8,0"
                                        CornerRadius="10" Background="Transparent" Cursor="Hand">
                                    <TextBlock x:Name="TabText" Text="{TemplateBinding Header}"
                                               FontSize="14" FontWeight="SemiBold"
                                               Foreground="{StaticResource TextMutedBrush}" />
                                </Border>
                                <ControlTemplate.Triggers>
                                    <Trigger Property="IsSelected" Value="True">
                                        <Setter TargetName="TabBorder" Property="Background"
                                                Value="{StaticResource PrimaryGhostBrush}" />
                                        <Setter TargetName="TabText" Property="Foreground"
                                                Value="{StaticResource PrimaryBrush}" />
                                    </Trigger>
                                    <Trigger Property="IsMouseOver" Value="True">
                                        <Setter TargetName="TabBorder" Property="Background"
                                                Value="{StaticResource PrimaryGhostBrush}" />
                                    </Trigger>
                                </ControlTemplate.Triggers>
                            </ControlTemplate>
                        </Setter.Value>
                    </Setter>
                </Style>
            </TabControl.Resources>

            <!-- Tab 1: Admin messages -->
            <TabItem x:Name="AdminTab" Header="הודעות ממנהל">
                <Grid>
                    <Grid.RowDefinitions>
                        <RowDefinition Height="*" />
                        <RowDefinition Height="Auto" />
                    </Grid.RowDefinitions>

                    <!-- Messages list -->
                    <Border Grid.Row="0" Background="White" CornerRadius="14"
                            Padding="0" Margin="0,12,0,12">
                        <Grid>
                            <!-- Loading -->
                            <StackPanel x:Name="AdminLoadingPanel" VerticalAlignment="Center"
                                        HorizontalAlignment="Center" Visibility="Visible">
                                <TextBlock Text="טוען הודעות..." FontSize="14"
                                           Foreground="{StaticResource TextMutedBrush}"
                                           HorizontalAlignment="Center" />
                            </StackPanel>

                            <!-- Empty -->
                            <StackPanel x:Name="AdminEmptyPanel" VerticalAlignment="Center"
                                        HorizontalAlignment="Center" Visibility="Collapsed">
                                <Border Width="64" Height="64" CornerRadius="32"
                                        Background="{StaticResource PrimaryGhostBrush}"
                                        HorizontalAlignment="Center" Margin="0,0,0,16">
                                    <TextBlock Text="&#xE8F2;" FontFamily="Segoe MDL2 Assets"
                                               FontSize="26" Foreground="{StaticResource PrimaryBrush}"
                                               HorizontalAlignment="Center" VerticalAlignment="Center" />
                                </Border>
                                <TextBlock Text="אין הודעות חדשות" FontSize="16" FontWeight="SemiBold"
                                           Foreground="{StaticResource TextPrimaryBrush}"
                                           HorizontalAlignment="Center" />
                                <TextBlock Text="הודעות ממנהל החנות יופיעו כאן"
                                           FontSize="13" Foreground="{StaticResource TextMutedBrush}"
                                           HorizontalAlignment="Center" Margin="0,6,0,0" />
                            </StackPanel>

                            <!-- List -->
                            <ScrollViewer x:Name="AdminScroll" VerticalScrollBarVisibility="Auto"
                                          Padding="20,16" Visibility="Collapsed">
                                <ItemsControl x:Name="AdminMessagesList">
                                    <ItemsControl.ItemTemplate>
                                        <DataTemplate>
                                            <Border Margin="0,0,0,14" CornerRadius="12"
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
                                                    </StackPanel>
                                                </Grid>
                                            </Border>
                                        </DataTemplate>
                                    </ItemsControl.ItemTemplate>
                                </ItemsControl>
                            </ScrollViewer>
                        </Grid>
                    </Border>

                    <!-- Send reply -->
                    <Border Grid.Row="1" Background="White" CornerRadius="14" Padding="16,12">
                        <Grid>
                            <Grid.ColumnDefinitions>
                                <ColumnDefinition Width="*" />
                                <ColumnDefinition Width="Auto" />
                            </Grid.ColumnDefinitions>
                            <Border Grid.Column="0" CornerRadius="10" Background="#F7F8FA"
                                    BorderBrush="#E8EAED" BorderThickness="1" Padding="12,8" Margin="0,0,10,0">
                                <TextBox x:Name="AdminReplyBox"
                                         Text="" AcceptsReturn="False"
                                         BorderThickness="0" Background="Transparent"
                                         FontSize="14" VerticalAlignment="Center"
                                         Tag="שלח תגובה למנהל..." />
                            </Border>
                            <Button Grid.Column="1" x:Name="AdminSendBtn"
                                    Click="AdminSendBtn_Click"
                                    Width="44" Height="44" Cursor="Hand">
                                <Button.Template>
                                    <ControlTemplate TargetType="Button">
                                        <Border x:Name="SendBg" CornerRadius="22" Width="44" Height="44">
                                            <Border.Background>
                                                <LinearGradientBrush StartPoint="0,0" EndPoint="1,1">
                                                    <GradientStop Color="#6366F1" Offset="0" />
                                                    <GradientStop Color="#8B5CF6" Offset="1" />
                                                </LinearGradientBrush>
                                            </Border.Background>
                                            <TextBlock Text="&#xE724;" FontFamily="Segoe MDL2 Assets"
                                                       FontSize="16" Foreground="White"
                                                       HorizontalAlignment="Center" VerticalAlignment="Center" />
                                        </Border>
                                        <ControlTemplate.Triggers>
                                            <Trigger Property="IsMouseOver" Value="True">
                                                <Setter TargetName="SendBg" Property="Opacity" Value="0.85" />
                                            </Trigger>
                                        </ControlTemplate.Triggers>
                                    </ControlTemplate>
                                </Button.Template>
                            </Button>
                        </Grid>
                    </Border>
                </Grid>
            </TabItem>

            <!-- Tab 2: Supervisor messages -->
            <TabItem x:Name="SupervisorTab" Header="הודעות מהפיקוח">
                <Grid>
                    <Grid.RowDefinitions>
                        <RowDefinition Height="*" />
                        <RowDefinition Height="Auto" />
                    </Grid.RowDefinitions>

                    <!-- Messages list -->
                    <Border Grid.Row="0" Background="White" CornerRadius="14"
                            Padding="0" Margin="0,12,0,12">
                        <Grid>
                            <!-- Loading -->
                            <StackPanel x:Name="SupervisorLoadingPanel" VerticalAlignment="Center"
                                        HorizontalAlignment="Center" Visibility="Visible">
                                <TextBlock Text="טוען הודעות..." FontSize="14"
                                           Foreground="{StaticResource TextMutedBrush}"
                                           HorizontalAlignment="Center" />
                            </StackPanel>

                            <!-- Empty -->
                            <StackPanel x:Name="SupervisorEmptyPanel" VerticalAlignment="Center"
                                        HorizontalAlignment="Center" Visibility="Collapsed">
                                <Border Width="64" Height="64" CornerRadius="32"
                                        Background="{StaticResource PrimaryGhostBrush}"
                                        HorizontalAlignment="Center" Margin="0,0,0,16">
                                    <TextBlock Text="&#xE8F2;" FontFamily="Segoe MDL2 Assets"
                                               FontSize="26" Foreground="{StaticResource PrimaryBrush}"
                                               HorizontalAlignment="Center" VerticalAlignment="Center" />
                                </Border>
                                <TextBlock Text="אין הודעות מהפיקוח" FontSize="16" FontWeight="SemiBold"
                                           Foreground="{StaticResource TextPrimaryBrush}"
                                           HorizontalAlignment="Center" />
                                <TextBlock Text="הודעות מהפיקוח יופיעו כאן"
                                           FontSize="13" Foreground="{StaticResource TextMutedBrush}"
                                           HorizontalAlignment="Center" Margin="0,6,0,0" />
                            </StackPanel>

                            <!-- List -->
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
                            </ScrollViewer>
                        </Grid>
                    </Border>

                    <!-- Send reply -->
                    <Border Grid.Row="1" Background="White" CornerRadius="14" Padding="16,12">
                        <Grid>
                            <Grid.ColumnDefinitions>
                                <ColumnDefinition Width="*" />
                                <ColumnDefinition Width="Auto" />
                            </Grid.ColumnDefinitions>
                            <Border Grid.Column="0" CornerRadius="10" Background="#F7F8FA"
                                    BorderBrush="#E8EAED" BorderThickness="1" Padding="12,8" Margin="0,0,10,0">
                                <TextBox x:Name="SupervisorReplyBox"
                                         Text="" AcceptsReturn="False"
                                         BorderThickness="0" Background="Transparent"
                                         FontSize="14" VerticalAlignment="Center"
                                         Tag="שלח תגובה לפיקוח..." />
                            </Border>
                            <Button Grid.Column="1" x:Name="SupervisorSendBtn"
                                    Click="SupervisorSendBtn_Click"
                                    Width="44" Height="44" Cursor="Hand">
                                <Button.Template>
                                    <ControlTemplate TargetType="Button">
                                        <Border x:Name="SendBg2" CornerRadius="22" Width="44" Height="44">
                                            <Border.Background>
                                                <LinearGradientBrush StartPoint="0,0" EndPoint="1,1">
                                                    <GradientStop Color="#059669" Offset="0" />
                                                    <GradientStop Color="#10B981" Offset="1" />
                                                </LinearGradientBrush>
                                            </Border.Background>
                                            <TextBlock Text="&#xE724;" FontFamily="Segoe MDL2 Assets"
                                                       FontSize="16" Foreground="White"
                                                       HorizontalAlignment="Center" VerticalAlignment="Center" />
                                        </Border>
                                        <ControlTemplate.Triggers>
                                            <Trigger Property="IsMouseOver" Value="True">
                                                <Setter TargetName="SendBg2" Property="Opacity" Value="0.85" />
                                            </Trigger>
                                        </ControlTemplate.Triggers>
                                    </ControlTemplate>
                                </Button.Template>
                            </Button>
                        </Grid>
                    </Border>
                </Grid>
            </TabItem>
        </TabControl>
    </Grid>
</Page>"""

open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml', 'w', encoding='utf-8').write(content)
print('OK')
