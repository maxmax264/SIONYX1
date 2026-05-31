# Fix XAML - add tab buttons and converter
xaml = open(r'.\src\SionyxKiosk\Views\Pages\HistoryPage.xaml', encoding='utf-8').read()

old_res = "    <Page.Resources>\n        <BooleanToVisibilityConverter x:Key=\"BoolToVis\" />\n    </Page.Resources>"
new_res = """    <Page.Resources>
        <BooleanToVisibilityConverter x:Key="BoolToVis" />
        <local:ZeroToVisibilityConverter x:Key="ZeroToVisConverter" />
    </Page.Resources>"""

# Add xmlns:local
old_ns = '      Title="היסטוריה" FlowDirection="RightToLeft">'
new_ns = '      xmlns:local="clr-namespace:SionyxKiosk.Views.Pages"\n      Title="היסטוריה" FlowDirection="RightToLeft">'

old_row2 = "            <RowDefinition Height=\"Auto\" />\n            <RowDefinition Height=\"Auto\" />\n            <RowDefinition Height=\"Auto\" />\n            <RowDefinition Height=\"*\" />"
new_row2 = "            <RowDefinition Height=\"Auto\" />\n            <RowDefinition Height=\"Auto\" />\n            <RowDefinition Height=\"Auto\" />\n            <RowDefinition Height=\"Auto\" />\n            <RowDefinition Height=\"*\" />"

old_scroll = "        <ScrollViewer Grid.Row=\"3\""
new_scroll = "        <!-- Tab buttons -->\n        <StackPanel Grid.Row=\"3\" Orientation=\"Horizontal\" Margin=\"0,0,0,16\">\n            <RadioButton Content=\"רכישות\" IsChecked=\"{Binding IsPurchasesTab}\" Style=\"{StaticResource TabRadioButton}\" GroupName=\"HistoryTabs\" IsChecked=\"True\" Margin=\"0,0,8,0\"/>\n            <RadioButton Content=\"שימוש\" IsChecked=\"{Binding IsSessionsTab}\" Style=\"{StaticResource TabRadioButton}\" GroupName=\"HistoryTabs\" Margin=\"0,0,8,0\"/>\n            <RadioButton Content=\"הדפסות\" IsChecked=\"{Binding IsPrintsTab}\" Style=\"{StaticResource TabRadioButton}\" GroupName=\"HistoryTabs\"/>\n        </StackPanel>\n        <ScrollViewer Grid.Row=\"4\""

c1 = xaml.count(old_ns)
print(f"NS: {c1}")
if c1 == 1: xaml = xaml.replace(old_ns, new_ns, 1)

c2 = xaml.count(old_res)
print(f"Res: {c2}")
if c2 == 1: xaml = xaml.replace(old_res, new_res, 1)

c3 = xaml.count(old_row2)
print(f"Rows: {c3}")
if c3 == 1: xaml = xaml.replace(old_row2, new_row2, 1)

c4 = xaml.count(old_scroll)
print(f"Scroll: {c4}")
if c4 == 1: xaml = xaml.replace(old_scroll, new_scroll, 1)

# Fix Grid.Row for sessions and prints tabs (they should be Row 4 now)
xaml = xaml.replace(
    '<ScrollViewer Grid.Row="3" Visibility="{Binding IsSessionsTabVisible',
    '<ScrollViewer Grid.Row="4" Visibility="{Binding IsSessionsTabVisible'
)
xaml = xaml.replace(
    '<ScrollViewer Grid.Row="3" Visibility="{Binding IsPrintsTabVisible',
    '<ScrollViewer Grid.Row="4" Visibility="{Binding IsPrintsTabVisible'
)

open(r'.\src\SionyxKiosk\Views\Pages\HistoryPage.xaml', 'w', encoding='utf-8').write(xaml)
print("XAML OK")

# Fix ViewModel - add tab properties
vm = open(r'.\src\SionyxKiosk\ViewModels\HistoryViewModel.cs', encoding='utf-8').read()

old_vm = "    [ObservableProperty] private int _totalSessionMinutes;\n    [ObservableProperty] private int _totalPrintPages;\n    [ObservableProperty] private double _totalPrintCost;"
new_vm = """    [ObservableProperty] private int _totalSessionMinutes;
    [ObservableProperty] private int _totalPrintPages;
    [ObservableProperty] private double _totalPrintCost;
    [ObservableProperty] private bool _isPurchasesTab = true;
    [ObservableProperty] private bool _isSessionsTab = false;
    [ObservableProperty] private bool _isPrintsTab = false;
    public bool IsPurchasesTabVisible => IsPurchasesTab;
    public bool IsSessionsTabVisible => IsSessionsTab;
    public bool IsPrintsTabVisible => IsPrintsTab;"""

cv = vm.count(old_vm)
print(f"VM: {cv}")
if cv == 1:
    vm = vm.replace(old_vm, new_vm, 1)

# Add OnTabChanged to refresh visibility
old_partial = "    partial void OnSearchTextChanged(string value) => FilteredPurchases.Refresh();"
new_partial = """    partial void OnSearchTextChanged(string value) => FilteredPurchases.Refresh();
    partial void OnIsPurchasesTabChanged(bool value) { OnPropertyChanged(nameof(IsPurchasesTabVisible)); OnPropertyChanged(nameof(IsSessionsTabVisible)); OnPropertyChanged(nameof(IsPrintsTabVisible)); }
    partial void OnIsSessionsTabChanged(bool value) { OnPropertyChanged(nameof(IsPurchasesTabVisible)); OnPropertyChanged(nameof(IsSessionsTabVisible)); OnPropertyChanged(nameof(IsPrintsTabVisible)); }
    partial void OnIsPrintsTabChanged(bool value) { OnPropertyChanged(nameof(IsPurchasesTabVisible)); OnPropertyChanged(nameof(IsSessionsTabVisible)); OnPropertyChanged(nameof(IsPrintsTabVisible)); }"""

cp = vm.count(old_partial)
print(f"Partial: {cp}")
if cp == 1:
    vm = vm.replace(old_partial, new_partial, 1)
    open(r'.\src\SionyxKiosk\ViewModels\HistoryViewModel.cs', 'w', encoding='utf-8').write(vm)
    print("VM OK")
else:
    print("VM partial NOT FOUND")
