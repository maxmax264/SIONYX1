path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs'

with open(path, 'rb') as f:
    raw = f.read()

lines = raw.split(b'\n')
bad_line_nums = [40, 358, 359, 399, 405, 431, 445, 464, 743, 744, 757, 775]

for n in bad_line_nums:
    line = lines[n-1]
    print(f"=== Line {n} (raw bytes) ===")
    print(line)
    print()
