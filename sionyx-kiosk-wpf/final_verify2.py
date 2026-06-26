path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs'
out_path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\final_verify_output2.txt'

with open(path, encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
check_lines = [40, 358, 359, 399, 405, 431, 445, 464, 743, 744, 757, 775]

with open(out_path, 'w', encoding='utf-8') as out:
    for n in check_lines:
        out.write(f"Line {n}: {lines[n-1]}\n")

print("Written directly from Python, no console involved")
