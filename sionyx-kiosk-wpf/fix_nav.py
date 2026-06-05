path = r'.\src\SionyxKiosk\Views\Windows\MainWindow.xaml.cs'
content = open(path, encoding='utf-8').read()
content = content.replace(
    '        Loaded += (_, _) =>\n        {\n            NavigateToPage("Home");\n            UpdateAvatarInitials();\n        };',
    '        Loaded += (_, _) =>\n        {\n            Dispatcher.InvokeAsync(() => NavigateToPage("Home"), System.Windows.Threading.DispatcherPriority.Loaded);\n            UpdateAvatarInitials();\n        };'
)
open(path, 'w', encoding='utf-8').write(content)
print('OK')
