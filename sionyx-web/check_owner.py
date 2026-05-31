import re
content = open(r'.\src\owner\pages\OwnerDashboardPage.jsx', encoding='utf-8').read()
matches = re.findall(r'\\u[0-9a-fA-F]{4}', content)
print(f"Found {len(matches)} unicode escapes")
if matches:
    print(matches[:10])
