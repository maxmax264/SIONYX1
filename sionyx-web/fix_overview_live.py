content = open(r'.\src\pages\OverviewPage.jsx', encoding='utf-8').read()

# Remove both slice(0, 5) limits
old1 = "          return dateB - dateA;\n        })\n        .slice(0, 5);\n      setRecentUsers(activeUsers);"
new1 = "          return dateB - dateA;\n        });\n      setRecentUsers(activeUsers);"

count1 = content.count(old1)
print(f"Step 1: {count1}")
if count1 == 2:
    content = content.replace(old1, new1)
    print("Step 1: OK")
elif count1 == 1:
    content = content.replace(old1, new1, 1)
    print("Step 1: OK (1 match)")
else:
    print("Step 1: NOT FOUND"); exit()

open(r'.\src\pages\OverviewPage.jsx', 'w', encoding='utf-8').write(content)
print("File written")
