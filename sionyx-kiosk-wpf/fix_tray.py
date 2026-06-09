import re
content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\TrayIconService.cs', encoding='utf-8').read()

old = '    public event Action? RestoreRequested;\n    public event Action? OpenControlPanelRequested;'
new = '    public event Action? RestoreRequested;\n    public event Action? OpenControlPanelRequested;\n    public event Action? ExitRequested;'
assert content.count(old) == 1, f"old1 not found"
content = content.replace(old, new)

old = '            menu.Items.Add(restoreItem);\n            menu.Items.Add(controlItem);\n            menu.FlowDirection = FlowDirection.RightToLeft;'
new = '''            var separator = new Separator();
            var exitItem = new MenuItem { Header = "\u05e6\u05d0 \u05de\u05d4\u05ea\u05d5\u05db\u05e0\u05d4", FlowDirection = FlowDirection.RightToLeft };
            exitItem.Click += (s, e) => ExitRequested?.Invoke();
            menu.Items.Add(restoreItem);
            menu.Items.Add(controlItem);
            menu.Items.Add(separator);
            menu.Items.Add(exitItem);
            menu.FlowDirection = FlowDirection.RightToLeft;'''
assert content.count(old) == 1, f"old2 not found"
content = content.replace(old, new)

open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\TrayIconService.cs', 'w', encoding='utf-8').write(content)
print('OK')
