import re
content = open(r'.\src\owner\pages\OwnerDashboardPage.jsx', encoding='utf-8').read()
escapes = re.findall(r'\\u[0-9a-fA-F]{4}', content)
print(f"Found {len(escapes)} escapes")
if escapes:
    content = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), content)
    open(r'.\src\owner\pages\OwnerDashboardPage.jsx', 'w', encoding='utf-8').write(content)
    print("Fixed")
else:
    print("No escapes")
