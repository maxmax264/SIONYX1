content = open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', encoding='utf-8').read()

old = '    </Window.Resources>'
new = '''        <!-- Dynamic primary button that uses OverlayGradient from Firebase -->
        <Style x:Key="BtnPrimaryDynamic" TargetType="Button" BasedOn="{StaticResource BtnPrimary}">
            <Setter Property="Template">
                <Setter.Value>
                    <ControlTemplate TargetType="Button">
                        <Border x:Name="border"
                                CornerRadius="12"
                                Background="{Binding OverlayGradient, RelativeSource={RelativeSource AncestorType=Window}}"
                                Padding="{TemplateBinding Padding}"
                                SnapsToDevicePixels="True">
                            <ContentPresenter HorizontalAlignment="Center" VerticalAlignment="Center"
                                              RecognizesAccessKey="True" />
                        </Border>
                        <ControlTemplate.Triggers>
                            <Trigger Property="IsEnabled" Value="False">
                                <Setter TargetName="border" Property="Background" Value="#D1D5DB" />
                                <Setter TargetName="border" Property="Opacity" Value="0.6" />
                            </Trigger>
                        </ControlTemplate.Triggers>
                    </ControlTemplate>
                </Setter.Value>
            </Setter>
        </Style>
    </Window.Resources>'''

if old in content:
    content = content.replace(old, new, 1)
    print("Added BtnPrimaryDynamic: OK")
else:
    print("NOT FOUND")

open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', 'w', encoding='utf-8').write(content)
