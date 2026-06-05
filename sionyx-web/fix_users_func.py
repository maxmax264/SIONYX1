content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\pages\UsersPage.jsx', encoding='utf-8').read()
old = "  const handleDeleteUser = record => {"
new = "  const handleVerifyPhone = async (record) => {\n    try {\n      const result = await verifyUserPhone(orgId, record.uid);\n      if (result.success) {\n        message.success(`${record.fullName || record.email} \u05d0\u05d5\u05de\u05ea \u05d1\u05d4\u05e6\u05dc\u05d7\u05d4`);\n      } else {\n        message.error('\u05e9\u05d2\u05d9\u05d0\u05d4 \u05d1\u05d0\u05d9\u05de\u05d5\u05ea: ' + result.error);\n      }\n    } catch (error) {\n      message.error('\u05e9\u05d2\u05d9\u05d0\u05d4 \u05d1\u05d0\u05d9\u05de\u05d5\u05ea');\n    }\n  };\n\n  const handleDeleteUser = record => {"
count = content.count(old)
print(f"function match: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\pages\UsersPage.jsx', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
