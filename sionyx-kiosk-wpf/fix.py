content = open(r'.\src\SionyxKiosk\App.xaml.cs', encoding='utf-8').read()

old = """                            _hasFrozenSession = clientWasActive;
                            if (MainWindow is Views.Windows.MainWindow mainWin && !clientWasActive)
                            { mainWin.AllowClose(); mainWin.Close(); }
                            else if (MainWindow is AuthWindow aw)
                            { aw.AllowClose(); aw.Close(); }"""

new = """                            _hasFrozenSession = clientWasActive;
                            if (MainWindow is Views.Windows.MainWindow mainWin && !clientWasActive)
                            { mainWin.AllowClose(); mainWin.Close(); }
                            else if (MainWindow is Views.Windows.MainWindow mainWinActive && clientWasActive)
                            { mainWinActive.Topmost = false; mainWinActive.WindowState = WindowState.Minimized; }
                            else if (MainWindow is AuthWindow aw)
                            { aw.AllowClose(); aw.Close(); }"""

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\App.xaml.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
