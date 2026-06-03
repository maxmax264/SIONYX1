f = open(r'.\src\SionyxKiosk\Views\Controls\PurchaseCard.xaml.cs', encoding='utf-8')
c = f.read()
f.close()

old = '    public static readonly DependencyProperty IsOperatorTopupProperty =\n        DependencyProperty.Register(nameof(IsOperatorTopup), typeof(bool), typeof(PurchaseCard), new PropertyMetadata(false));\n    public static readonly DependencyProperty IsOperatorTopupVisibleProperty =\n        DependencyProperty.Register(nameof(IsOperatorTopupVisible), typeof(Visibility), typeof(PurchaseCard), new PropertyMetadata(Visibility.Collapsed));\n    public bool IsOperatorTopup { get => (bool)GetValue(IsOperatorTopupProperty); set { SetValue(IsOperatorTopupProperty, value); IsOperatorTopupVisible = value ? Visibility.Visible : Visibility.Collapsed; } }\n    public Visibility IsOperatorTopupVisible { get => (Visibility)GetValue(IsOperatorTopupVisibleProperty); set => SetValue(IsOperatorTopupVisibleProperty, value); }'

new = '    public static readonly DependencyProperty IsOperatorTopupVisibleProperty =\n        DependencyProperty.Register(nameof(IsOperatorTopupVisible), typeof(Visibility), typeof(PurchaseCard), new PropertyMetadata(Visibility.Collapsed));\n    public static readonly DependencyProperty IsOperatorTopupProperty =\n        DependencyProperty.Register(nameof(IsOperatorTopup), typeof(bool), typeof(PurchaseCard), new PropertyMetadata(false, (d, e) => {\n            if (d is PurchaseCard card) card.IsOperatorTopupVisible = (bool)e.NewValue ? Visibility.Visible : Visibility.Collapsed;\n        }));\n    public bool IsOperatorTopup { get => (bool)GetValue(IsOperatorTopupProperty); set => SetValue(IsOperatorTopupProperty, value); }\n    public Visibility IsOperatorTopupVisible { get => (Visibility)GetValue(IsOperatorTopupVisibleProperty); set => SetValue(IsOperatorTopupVisibleProperty, value); }'

count = c.count(old)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Controls\PurchaseCard.xaml.cs', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
