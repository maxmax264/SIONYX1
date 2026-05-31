content = open(r'.\src\components\settings\KioskBackgroundSettings.jsx', encoding='utf-8').read()
import re
escapes = re.findall(r'\\u[0-9a-fA-F]{4}', content)
print(f"Found {len(escapes)} escapes")
if escapes:
    print(escapes[:5])
    def replace_escape(m):
        return chr(int(m.group(0)[2:], 16))
    content = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), content)
    open(r'.\src\components\settings\KioskBackgroundSettings.jsx', 'w', encoding='utf-8').write(content)
    print("Fixed")
else:
    print("No escapes - checking raw bytes...")
    raw = open(r'.\src\components\settings\KioskBackgroundSettings.jsx', 'rb').read()
    print(raw[1500:1700])
