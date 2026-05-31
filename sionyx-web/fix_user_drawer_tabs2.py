content = open(r'.\src\pages\UsersPage.jsx', encoding='utf-8').read()

old2 = "  Select,\n} from 'antd';"
new2 = "  Select,\n  Tabs,\n} from 'antd';"
c2 = content.count(old2)
print(f"Step 2: {c2}")
if c2 == 1:
    content = content.replace(old2, new2, 1)
    open(r'.\src\pages\UsersPage.jsx', 'w', encoding='utf-8').write(content)
    print("Step 2: OK - file written")
else:
    print("Step 2: NOT FOUND")
