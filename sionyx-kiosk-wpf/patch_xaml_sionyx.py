import sys

path = r"src\SionyxKiosk\Views\Windows\AuthWindow.xaml"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add SIONYX above WelcomeText in login form
old1 = '                        <StackPanel VerticalAlignment="Center" Margin="60,60">\n                            <TextBlock Text="{Binding WelcomeText}" Style="{StaticResource TextH1}" Margin="0,0,0,6" />'
new1 = '                        <StackPanel VerticalAlignment="Center" Margin="60,60">\n                            <TextBlock Text="SIONYX" FontSize="28" FontWeight="ExtraBold"\n                                       Foreground="{Binding OverlayGradient}"\n                                       HorizontalAlignment="Center" Margin="0,0,0,20"\n                                       Visibility="{Binding CleanMode, Converter={StaticResource BoolToVis}}" />\n                            <TextBlock Text="{Binding WelcomeText}" Style="{StaticResource TextH1}" Margin="0,0,0,6" />'

if old1 not in content:
    print("ERROR: login form target not found")
    sys.exit(1)

content = content.replace(old1, new1, 1)

# 2. Add version watermark bottom-left of main screen (outside Viewbox, inside main Grid)
old2 = '        <Image x:Name="BgImage"'
new2 = '''        <!-- Bottom-left version watermark -->
        <StackPanel VerticalAlignment="Bottom" HorizontalAlignment="Left"
                    Margin="16,0,0,12" Orientation="Horizontal" Panel.ZIndex="10">
            <TextBlock Text="SIONYX" FontSize="12" FontWeight="Bold"
                       Foreground="#99FFFFFF" Margin="0,0,6,0" />
            <TextBlock Text="{Binding AppVersion}" FontSize="12"
                       Foreground="#66FFFFFF" />
        </StackPanel>

        <Image x:Name="BgImage"'''

if old2 not in content:
    print("ERROR: BgImage target not found")
    sys.exit(1)

content = content.replace(old2, new2, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched successfully!")
