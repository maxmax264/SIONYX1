content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\pages\SettingsPage.jsx', encoding='utf-8').read()

old = "import { SettingOutlined, DollarOutlined, DownloadOutlined, PhoneOutlined, LockOutlined, MessageOutlined } from '@ant-design/icons';"
new = "import { SettingOutlined, DollarOutlined, DownloadOutlined, PhoneOutlined, LockOutlined, MessageOutlined, CreditCardOutlined } from '@ant-design/icons';"
content = content.replace(old, new, 1)

old = "import KioskPasswordSettings from '../components/settings/KioskPasswordSettings';"
new = "import KioskPasswordSettings from '../components/settings/KioskPasswordSettings';\nimport PaymentSettings from '../components/settings/PaymentSettings';"
content = content.replace(old, new, 1)

old = "    {\n      key: 'downloads',"
new = """    {
      key: 'payment',
      label: (
        <span>
          <CreditCardOutlined />
          {' '}תשלום
        </span>
      ),
      children: <PaymentSettings />,
    },
    {
      key: 'downloads',"""
content = content.replace(old, new, 1)

open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\pages\SettingsPage.jsx', 'w', encoding='utf-8').write(content)
print('OK')
