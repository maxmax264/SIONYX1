content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\HomeViewModel.cs', encoding='utf-8').read()
old = '        _ = LoadUnreadCountAsync();\n        _ = LoadAnnouncementsAsync();\n    }'
new = '''        _ = LoadUnreadCountAsync();
        _ = LoadAnnouncementsAsync();
    }

    /// <summary>Called on each new login to refresh user data.</summary>
    public void Reinitialize(UserData user)
    {
        _user = user;
        WelcomeMessage = $"שלום, {_user.FullName}!";
        IsSessionActive = _session.IsActive;
        HasNoTime = _user.RemainingTime <= 0;
        PrimaryButtonText = HasNoTime ? "רכוש חבילה" : "▶  התחל הפעלה";
        ErrorMessage = "";
        UpdateStats();
        _ = LoadUnreadCountAsync();
        _ = LoadAnnouncementsAsync();
    }'''
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\HomeViewModel.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
