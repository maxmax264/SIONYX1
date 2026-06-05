content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\pages\SettingsPage.jsx', encoding='utf-8').read()
old = "import { SettingOutlined, DollarOutlined, DownloadOutlined } from '@ant-design/icons';"
new = "import { SettingOutlined, DollarOutlined, DownloadOutlined, PhoneOutlined } from '@ant-design/icons';"
count = content.count(old)
print(f"icons match: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\pages\SettingsPage.jsx', 'w', encoding='utf-8').write(content)
    print('icons OK')
else:
    print('NOT FOUND')
