path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs'

with open(path, 'rb') as f:
    raw = f.read()

lines = raw.split(b'\n')
fixed_count = 0
for i, line in enumerate(lines):
    try:
        line.decode('utf-8')
    except UnicodeDecodeError:
        decoded = line.decode('cp1255')
        lines[i] = decoded.encode('utf-8')
        fixed_count += 1

print(f"Fixed {fixed_count} lines")

fixed_raw = b'\n'.join(lines)
content = fixed_raw.decode('utf-8')
print("Re-decoded successfully, length:", len(content))

with open(path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print("Saved encoding-fixed file")
