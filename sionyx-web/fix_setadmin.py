content = open(r'.\src\App.jsx', encoding='utf-8').read()

old = "      } else {\n        setAdmin(null);\n      }"
new = "      } else {\n        setUser(null);\n      }"

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\App.jsx', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
