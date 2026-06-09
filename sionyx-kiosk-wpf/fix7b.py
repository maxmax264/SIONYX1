content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\TrayIconService.cs', encoding='utf-8').read()

old = '    public event Action? OpenControlPanelRequested;\n    public event Action? AboutRequested;'
new = '    public event Action? OpenControlPanelRequested;\n    public event Action? OpenDashboardRequested;\n    public event Action? AboutRequested;'
assert content.count(old) == 1, "events not found"
content = content.replace(old, new)

old = '            var aboutItem = new MenuItem { Header = "\u05d0\u05d5\u05d3\u05d5\u05ea", FlowDirection = FlowDirection.RightToLeft };\n            aboutItem.Click += (s, e) => AboutRequested?.Invoke();\n            menu.Items.Add(restoreItem);\n            menu.Items.Add(controlItem);\n            menu.Items.Add(aboutItem);'
new = '            var dashItem = new MenuItem { Header = "\u05e4\u05ea\u05d7 \u05d3\u05e9\u05d1\u05d5\u05e8\u05d3", FlowDirection = FlowDirection.RightToLeft };\n            dashItem.Click += (s, e) => OpenDashboardRequested?.Invoke();\n            var aboutItem = new MenuItem { Header = "\u05d0\u05d5\u05d3\u05d5\u05ea", FlowDirection = FlowDirection.RightToLeft };\n            aboutItem.Click += (s, e) => AboutRequested?.Invoke();\n            menu.Items.Add(restoreItem);\n            menu.Items.Add(controlItem);\n            menu.Items.Add(dashItem);\n            menu.Items.Add(aboutItem);'
assert content.count(old) == 1, "menu not found"
content = content.replace(old, new)

open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\TrayIconService.cs', 'w', encoding='utf-8').write(content)
print('OK')
