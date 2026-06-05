content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\pages\UsersPage.jsx', encoding='utf-8').read()
old = "  DeleteOutlined,\n  PhoneOutlined,"
new = "  DeleteOutlined,"
count = content.count(old)
print(f"match: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\pages\UsersPage.jsx', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
