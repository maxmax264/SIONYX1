f = open(r'.\src\SionyxKiosk\Views\Controls\PurchaseCard.xaml.cs', encoding='utf-8')
c = f.read()
f.close()

old = '    public PurchaseCard() { InitializeComponent(); }'
new = '''    public static readonly DependencyProperty IsOperatorTopupProperty =
        DependencyProperty.Register(nameof(IsOperatorTopup), typeof(bool), typeof(PurchaseCard), new PropertyMetadata(false));
    public static readonly DependencyProperty IsOperatorTopupVisibleProperty =
        DependencyProperty.Register(nameof(IsOperatorTopupVisible), typeof(Visibility), typeof(PurchaseCard), new PropertyMetadata(Visibility.Collapsed));
    public bool IsOperatorTopup { get => (bool)GetValue(IsOperatorTopupProperty); set { SetValue(IsOperatorTopupProperty, value); IsOperatorTopupVisible = value ? Visibility.Visible : Visibility.Collapsed; } }
    public Visibility IsOperatorTopupVisible { get => (Visibility)GetValue(IsOperatorTopupVisibleProperty); set => SetValue(IsOperatorTopupVisibleProperty, value); }

    public PurchaseCard() { InitializeComponent(); }'''

count = c.count(old)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Controls\PurchaseCard.xaml.cs', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
