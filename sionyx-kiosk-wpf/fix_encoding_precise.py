path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs'

with open(path, 'rb') as f:
    raw = f.read()

lines = raw.split(b'\n')

# Group A: full cp1255 lines (genuine Hebrew text)
group_a = [40, 358, 359, 743, 744, 757, 775]
# Group B: single 0x97 byte = Windows-1252 em dash, NOT Hebrew
group_b = [399, 405, 431, 445, 464]

for n in group_a:
    idx = n - 1
    decoded = lines[idx].decode('cp1255')
    lines[idx] = decoded.encode('utf-8')
    print(f"Line {n} (cp1255->utf8):", decoded)

for n in group_b:
    idx = n - 1
    # Replace the single 0x97 byte with UTF-8 em dash, decode rest as utf-8/ascii
    fixed_bytes = lines[idx].replace(b'\x97', '—'.encode('utf-8'))
    decoded = fixed_bytes.decode('utf-8')  # should succeed now
    lines[idx] = fixed_bytes
    print(f"Line {n} (0x97->em dash):", decoded)

fixed_raw = b'\n'.join(lines)
# Verify whole file decodes now
content = fixed_raw.decode('utf-8')
print()
print("Full file re-decoded OK, length:", len(content))

with open(path, 'wb') as f:
    f.write(fixed_raw)
print("Saved.")
