f=open(r'.\src\pages\SettingsPage.jsx', encoding='utf-8')
c=f.read()
f.close()

old="import { SettingOutlined, DollarOutlined, DownloadOutlined, PictureOutlined, BgColorsOutlined } from '@ant-design/icons';"
new="import { SettingOutlined, DollarOutlined, DownloadOutlined } from '@ant-design/icons';"
assert c.count(old)==1
c=c.replace(old,new,1)

old="import KioskBackgroundSettings from '../components/settings/KioskBackgroundSettings';\nimport AuthDesignSettings from '../components/settings/AuthDesignSettings';"
new="import KioskDesignSettings from '../components/settings/KioskDesignSettings';"
assert c.count(old)==1
c=c.replace(old,new,1)

old="""    {
      key: 'background',
      label: (
        <span>
          <PictureOutlined />
          {' '}תמונת רקע
        </span>
      ),
      children: <KioskBackgroundSettings />,
    },"""
new=""
assert c.count(old)==1
c=c.replace(old,new,1)

old="""    {
      key: 'authdesign',
      label: (
        <span>
          <BgColorsOutlined />
          {' '}עיצוב מסך כניסה
        </span>
      ),
      children: <AuthDesignSettings />,
    },"""
new="""    {
      key: 'kioskdesign',
      label: (
        <span>
          <DownloadOutlined />
          {' '}עיצוב מסך כניסה
        </span>
      ),
      children: <KioskDesignSettings />,
    },"""
assert c.count(old)==1
c=c.replace(old,new,1)

open(r'.\src\pages\SettingsPage.jsx','w',encoding='utf-8').write(c)
print("OK")
