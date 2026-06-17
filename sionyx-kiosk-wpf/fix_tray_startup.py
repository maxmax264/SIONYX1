content = open(r'.\src\SionyxKiosk\Services\TrayIconService.cs', encoding='utf-8').read()

# Add event
old1 = '    public event Action? SettingsRequested;'
new1 = '    public event Action? SettingsRequested;\n    public event Action? StartupSettingsRequested;'

count1 = content.count(old1)
print(f"Fix 1: {count1} matches")
if count1 == 1:
    content = content.replace(old1, new1, 1)
    print("Fix 1 OK")
else:
    print("Fix 1 NOT FOUND")

# Add menu item before settings
old2 = '''            var settingsItem = new MenuItem { Header = "הגדרות", FlowDirection = FlowDirection.RightToLeft };
            settingsItem.Click += (s, e) => SettingsRequested?.Invoke();
            menu.Items.Add(settingsItem);'''
new2 = '''            var startupItem = new MenuItem { Header = "הגדרות הפעלה אוטומטית", FlowDirection = FlowDirection.RightToLeft };
            startupItem.Click += (s, e) => StartupSettingsRequested?.Invoke();
            menu.Items.Add(startupItem);
            var settingsItem = new MenuItem { Header = "הגדרות", FlowDirection = FlowDirection.RightToLeft };
            settingsItem.Click += (s, e) => SettingsRequested?.Invoke();
            menu.Items.Add(settingsItem);'''

count2 = content.count(old2)
print(f"Fix 2: {count2} matches")
if count2 == 1:
    content = content.replace(old2, new2, 1)
    print("Fix 2 OK")
else:
    print("Fix 2 NOT FOUND")

open(r'.\src\SionyxKiosk\Services\TrayIconService.cs', 'w', encoding='utf-8').write(content)
print("DONE")
