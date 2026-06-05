content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\pages\UsersPage.jsx', encoding='utf-8').read()

old = "      ...(!userRecord.isAdmin && userRecord.uid !== user?.uid\n        ? [\n            { type: 'divider' },\n            {\n              key: 'delete',"

new = "      {\n        key: 'verifyPhone',\n        icon: <PhoneOutlined />,\n        label: userRecord.phoneVerified ? 'טלפון מאומת' : 'אמת ידנית',\n        disabled: userRecord.phoneVerified === true,\n        onClick: () => handleVerifyPhone(userRecord),\n      },\n      ...(!userRecord.isAdmin && userRecord.uid !== user?.uid\n        ? [\n            { type: 'divider' },\n            {\n              key: 'delete',"

count = content.count(old)
print(f"match: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\pages\UsersPage.jsx', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
