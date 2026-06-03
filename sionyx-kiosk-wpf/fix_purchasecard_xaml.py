f = open(r'.\src\SionyxKiosk\Views\Controls\PurchaseCard.xaml', encoding='utf-8')
c = f.read()
f.close()

old = '''                <TextBlock Text="{Binding FormattedDate, RelativeSource={RelativeSource AncestorType=UserControl}}"
                           FontSize="{StaticResource FontSizeBase}" Foreground="{StaticResource TextMutedBrush}"
                           Margin="0,6,0,0" TextTrimming="CharacterEllipsis" />'''

new = '''                <TextBlock Text="{Binding FormattedDate, RelativeSource={RelativeSource AncestorType=UserControl}}"
                           FontSize="{StaticResource FontSizeBase}" Foreground="{StaticResource TextMutedBrush}"
                           Margin="0,6,0,0" TextTrimming="CharacterEllipsis" />
                <Border CornerRadius="8" Padding="10,4" Margin="0,6,0,0"
                        Background="#DBEAFE"
                        Visibility="{Binding IsOperatorTopupVisible, RelativeSource={RelativeSource AncestorType=UserControl}}"
                        HorizontalAlignment="Right">
                    <TextBlock Text="\u05d8\u05e2\u05d9\u05e0\u05ea \u05de\u05e4\u05e2\u05d9\u05dc" FontSize="12" Foreground="#1D4ED8" FontWeight="SemiBold"/>
                </Border>'''

count = c.count(old)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Controls\PurchaseCard.xaml', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
