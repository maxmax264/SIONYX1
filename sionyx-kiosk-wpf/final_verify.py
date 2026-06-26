path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs'
with open(path, encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
check_lines = [40, 358, 359, 399, 405, 431, 445, 464, 743, 744, 757, 775]
for n in check_lines:
    print(f"Line {n}: {lines[n-1]}")
