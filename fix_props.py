content = open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8').read()

lines_to_remove = [
    '    [ObservableProperty] private double _formX = 500;\n',
    '    [ObservableProperty] private double _formY = 0;\n',
    '    [ObservableProperty] private double _formWidth = 500;\n',
]

removed = 0
for line in lines_to_remove:
    if line in content:
        content = content.replace(line, '')
        removed += 1
        print(f"Removed: {line.strip()}")
    elif line.replace('\n', '\r\n') in content:
        content = content.replace(line.replace('\n', '\r\n'), '')
        removed += 1
        print(f"Removed CRLF: {line.strip()}")
    else:
        print(f"NOT FOUND: {line.strip()}")

print(f"Total: {removed}/3")
open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\AuthViewModel.cs', 'w', encoding='utf-8').write(content)
