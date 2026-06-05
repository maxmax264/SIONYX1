content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\pages\SettingsPage.jsx', encoding='utf-8').read()
old = "    {\n      key: 'downloads',"
new = "    {\n      key: 'phone',\n      label: (\n        <span>\n          <PhoneOutlined />\n          {' '}אימות טלפון\n        </span>\n      ),\n      children: <PhoneVerificationSettings />,\n    },\n    {\n      key: 'downloads',"
count = content.count(old)
print(f"tab match: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\pages\SettingsPage.jsx', 'w', encoding='utf-8').write(content)
    print('tab OK')
else:
    print('NOT FOUND - check encoding')
