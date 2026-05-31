f=open(r'.\src\pages\SettingsPage.jsx', encoding='utf-8')
c=f.read()
f.close()

old = "import PricingSettings from '../components/settings/PricingSettings';"
new = "import PricingSettings from '../components/settings/PricingSettings';\nimport KioskBackgroundSettings from '../components/settings/KioskBackgroundSettings';"
c = c.replace(old, new, 1)

old2 = "import { SettingOutlined, DollarOutlined, DownloadOutlined } from '@ant-design/icons';"
new2 = "import { SettingOutlined, DollarOutlined, DownloadOutlined, PictureOutlined } from '@ant-design/icons';"
c = c.replace(old2, new2, 1)

old3 = """    {
      key: 'downloads',"""
new3 = """    {
      key: 'background',
      label: (
        <span>
          <PictureOutlined />
          {' '}\u05ea\u05de\u05d5\u05e0\u05ea \u05e8\u05e7\u05e2
        </span>
      ),
      children: <KioskBackgroundSettings />,
    },
    {
      key: 'downloads',"""
c = c.replace(old3, new3, 1)

open(r'.\src\pages\SettingsPage.jsx', 'w', encoding='utf-8').write(c)
print("OK")
