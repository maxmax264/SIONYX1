content = open(r'.\src\SionyxKiosk\Services\TrayIconService.cs', encoding='utf-8').read()

# Add version parameter to Show method
old1 = '    public void Show()'
new1 = '    public void Show(string version = "")'

count1 = content.count(old1)
print(f"Fix 1: {count1} matches")
if count1 == 1:
    content = content.replace(old1, new1, 1)
    print("Fix 1 OK")
else:
    print("Fix 1 NOT FOUND")

# Add version item at top of menu
old2 = '''            var menu = new ContextMenu();
            var restoreItem = new MenuItem { Header = "׳"׳—׳–׳¨ ׳׳× ׳"׳×׳•׳›׳ ׳"", FlowDirection = FlowDirection.RightToLeft };'''
new2 = '''            var menu = new ContextMenu();
            if (!string.IsNullOrEmpty(version))
            {
                var versionItem = new MenuItem
                {
                    Header = $"SIONYX v{version}",
                    FlowDirection = FlowDirection.RightToLeft,
                    IsEnabled = false,
                    FontWeight = System.Windows.FontWeights.Bold
                };
                menu.Items.Add(versionItem);
                menu.Items.Add(new Separator());
            }
            var restoreItem = new MenuItem { Header = "׳"׳—׳–׳¨ ׳׳× ׳"׳×׳•׳›׳ ׳"", FlowDirection = FlowDirection.RightToLeft };'''

count2 = content.count(old2)
print(f"Fix 2: {count2} matches")
if count2 == 1:
    content = content.replace(old2, new2, 1)
    print("Fix 2 OK")
else:
    print("Fix 2 NOT FOUND")

open(r'.\src\SionyxKiosk\Services\TrayIconService.cs', 'w', encoding='utf-8').write(content)
print("DONE")
