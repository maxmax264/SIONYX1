with open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs', 'rb') as f:
    raw = f.read()

print("Total bytes:", len(raw))
print("Byte at 1302:", hex(raw[1302]))
print("Context bytes 1280-1330:", raw[1280:1330])

# count non-utf8 decodable lines
import re
lines = raw.split(b'\n')
bad_lines = []
for i, line in enumerate(lines):
    try:
        line.decode('utf-8')
    except UnicodeDecodeError:
        bad_lines.append(i+1)

print(f"Total lines: {len(lines)}")
print(f"Lines with invalid UTF-8: {len(bad_lines)}")
print("First 20 bad line numbers:", bad_lines[:20])
