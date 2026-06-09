content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\TrayIconService.cs', encoding='utf-8').read()

old = '    public event Action? RestoreRequested;\n    public event Action? OpenControlPanelRequested;\n    public event Action? ExitRequested;'
new = '    public event Action? RestoreRequested;\n    public event Action? OpenControlPanelRequested;\n    public event Action? AboutRequested;\n    public event Action? ExitRequested;'
assert content.count(old) == 1, "events not found"
content = content.replace(old, new)

old = '            menu.Items.Add(restoreItem);\n            menu.Items.Add(controlItem);\n            menu.Items.Add(separator);\n            menu.Items.Add(exitItem);'
new = '            var aboutItem = new MenuItem { Header = "\u05d0\u05d5\u05d3\u05d5\u05ea", FlowDirection = FlowDirection.RightToLeft };\n            aboutItem.Click += (s, e) => AboutRequested?.Invoke();\n            menu.Items.Add(restoreItem);\n            menu.Items.Add(controlItem);\n            menu.Items.Add(aboutItem);\n            menu.Items.Add(new Separator());\n            menu.Items.Add(exitItem);'
assert content.count(old) == 1, "menu not found"
content = content.replace(old, new)

open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\TrayIconService.cs', 'w', encoding='utf-8').write(content)
print('OK')
