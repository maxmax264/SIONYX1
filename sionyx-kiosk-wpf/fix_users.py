content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\StartupSettingsDialog.cs', encoding='utf-8').read()

old = '        if (users.Count == 0)\n            users.Add(Environment.UserName);\n\n        return users;'

new = '''        // Filter out system accounts
        users.RemoveAll(u => u.Equals("Administrator", System.StringComparison.OrdinalIgnoreCase)
            || u.Equals("Guest", System.StringComparison.OrdinalIgnoreCase)
            || u.Equals("DefaultAccount", System.StringComparison.OrdinalIgnoreCase)
            || u.Equals("WDAGUtilityAccount", System.StringComparison.OrdinalIgnoreCase));

        if (users.Count == 0)
            users.Add(Environment.UserName);

        return users;'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\StartupSettingsDialog.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print("Not found")
