content = open(r'.\src\SionyxKiosk\Services\TrayIconService.cs', encoding='utf-8').read()

old = 'var menu = new ContextMenu();\n            var restoreItem = new MenuItem { Header = "החזר את התוכנה", FlowDirection = FlowDirection.RightToLeft };'

new = '''var menu = new ContextMenu();
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
            var restoreItem = new MenuItem { Header = "החזר את התוכנה", FlowDirection = FlowDirection.RightToLeft };'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\TrayIconService.cs', 'w', encoding='utf-8').write(content)
    print("DONE")
else:
    print("NOT FOUND")
